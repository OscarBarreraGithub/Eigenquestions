"""Dated allocation update with the exact frozen F. No embedding or layout fit."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy import sparse


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    ap = argparse.ArgumentParser()
    for key in ['input', 'previous-input', 'previous-flow', 'schematic', 'out']:
        ap.add_argument('--' + key, type=Path, required=True)
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    data = json.loads(args.input.read_text()); old = json.loads(args.previous_input.read_text())
    previous = json.loads(args.schematic.read_text())
    assert sha(args.previous_input) == '738f78084a1908a8c7e3057021d400319ef1044344ecbaeaccf71f4d999f3bff'
    assert sha(args.previous_flow) == '7cc2f9c820ac6efb87577a0337611b86e0f3c7575dfbc5c70fa1a83b9ac0e4da'
    inventory = data['sourceMassInventory']; old_inventory = old['sourceMassInventory']
    assert len(inventory) == len(old_inventory) == 8473
    for a, b in zip(inventory, old_inventory):
        for key in ['unitId', 'paperId', 'sourceRow', 'textSha256', 'paperBalancedMass']:
            assert a[key] == b[key], (key, a['unitId'])
    lookup = {r['unitId']: i for i, r in enumerate(inventory)}
    mass = np.array([r['paperBalancedMass'] for r in inventory])
    F = sparse.load_npz(args.previous_flow)
    assert F.shape == (8473, 8473)
    assert np.max(abs(np.asarray(F.sum(axis=1)).ravel() - mass)) < 1e-10
    ids = sorted({r['destinationId'] for r in data['allocations']}); columns = {d: i for i, d in enumerate(ids)}
    H = sparse.csr_matrix(([r['weight'] for r in data['allocations']], ([lookup[r['unitId']] for r in data['allocations']], [columns[r['destinationId']] for r in data['allocations']])), shape=(8473, len(ids)))
    allocated = np.array([r['allocationStatus'] == 'resolved' for r in inventory]); sums = np.asarray(H.sum(axis=1)).ravel()
    assert allocated.sum() == 8436 and np.max(abs(sums[allocated] - 1)) < 1e-12 and not np.any(sums[~allocated])
    C = (H.T @ F @ H).tocsr(); zero = ~allocated
    full = float(F.sum()); represented = float(C.sum()); cross = float(F[allocated][:, zero].sum()); zero_zero = float(F[zero][:, zero].sum())
    assert abs(full - represented - 2 * cross - zero_zero) < 1e-8
    dest = {d['id']: d for d in data['destinations']}; children = {d: set() for d in dest}
    for d in dest.values():
        for p in d['parentIds']:
            children[p].add(d['id'])
    def descendants(id):
        result = {id}; todo = [id]
        while todo:
            for child in children[todo.pop()]:
                if child not in result:
                    result.add(child); todo.append(child)
        return result
    support = []
    for node in previous['nodes']:
        if node.get('metadataOnly'):
            support.append({'destinationId': node['destinationId'], 'mass': 0, 'sourceCount': 0}); continue
        cols = [columns[d] for d in descendants(node['destinationId']) if d in columns]
        weights = np.minimum(np.asarray(H[:, cols].sum(axis=1)).ravel(), 1)
        assert weights.any(), 'Approved schematic entry lost all admitted support'
        support.append({'destinationId': node['destinationId'], 'mass': float((weights * mass).sum()), 'sourceCount': int(np.count_nonzero(weights))})
    sparse.save_npz(args.out / 'accepted-H.npz', H); sparse.save_npz(args.out / 'complete-C.npz', C)
    dump(args.out / 'atom-ids.json', ids); dump(args.out / 'entry-support.json', support)
    diagnostics = {'membershipSha256': sha(args.input), 'previousMembershipSha256': sha(args.previous_input), 'fullFUnchanged': True, 'fullF': {'path': str(args.previous_flow), 'sha256': sha(args.previous_flow)}, 'counts': {'questionSources': 8473, 'allocated': 8436, 'unresolved': 37, 'reserved': 0, 'allocationBases': len(ids)}, 'mass': {**data['coverage']['sourceMass'], 'fullFMass': full, 'CRepresentedFlow': represented, 'assignedToZeroHFlowOneDirection': cross, 'zeroHToZeroHFlow': zero_zero, 'totalFlowOutsideC': full - represented}, 'invariants': {'maximumHRowError': float(np.max(abs(sums[allocated] - 1))), 'maximumFRowMassError': float(np.max(abs(np.asarray(F.sum(axis=1)).ravel() - mass))), 'globalMassRenormalized': False, 'newMetricFitPerformed': False, 'scientificRoutesAltered': False}, 'displayMeaning': 'Schematic coordinates and recorded entrance arcs are unchanged. Only exact current membership/support counts and provenance are updated. Previous stress/recall diagnostics remain bound to the previous H.'}
    dump(args.out / 'diagnostics.json', diagnostics)
    dump(args.out / 'manifest.json', {'schemaVersion': 'q025-dated-HC-update/1', 'membershipSha256': sha(args.input), 'previousMembershipSha256': sha(args.previous_input), 'unchangedF': diagnostics['fullF'], 'scriptSha256': sha(__file__), 'files': {p.name: {'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(args.out.iterdir()) if p.is_file() and p.name != 'manifest.json'}})
    print(json.dumps(diagnostics, indent=2))


if __name__ == '__main__':
    main()
