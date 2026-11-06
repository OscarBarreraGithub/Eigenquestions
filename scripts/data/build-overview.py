#!/usr/bin/env python3
"""Export the pinned Q-006 question overview without fitting or regrouping data.

python3 scripts/data/build-overview.py --source /path/to/publication-v1/map-data.json
Add --check to verify that the committed projection is byte-identical.
Only Python's standard library is required. Source archives are read-only.
"""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = 'graph-design/20261105-v1/publication-v1/map-data.json'
SOURCE_SHA256 = 'a6cb5cdb6d955d3ca33b9297be0a301ea50c6c8c75ba2294999adac8163d765b'
RELEASE_SHA256 = '907ab3ff3ce99744908d97ab185aaee34ab7f6a869a9b854b2cd302b3b3a7414'
VIEW_ID = 'minilm-leiden:physical_question:reviewed'
SHARD_SIZE = 512
MAX_INITIAL_BYTES = 3_000_000
POINT_COLUMNS = ['unitId', 'paperIndex', 'x', 'y', 'mass', 'homes']
PAPER_COLUMNS = ['paperId', 'title', 'url']

# Display edits only: original labels, memberships, and scientific coordinates
# remain exact. Every caption has an explicit, source-grounded rationale.
CAPTIONS = {
    'Questions across the collection': (
        'Questions across the collection', 'The original collection label is already concise.'),
    'String compactifications: effective theories, vacuum constraints and moduli limits': (
        'String compactifications', 'Retain the common subject; the full label preserves the effective-theory, vacuum and moduli distinctions.'),
    'Black-hole response and entropy: model dependence and quantum-gravity constraints': (
        'Quantum gravity, horizons & consistency', 'The supplied children include effective-theory consistency, de Sitter, holography, wormholes and black-hole extremality. This wider caption covers that actual umbrella without implying all children are black-hole calculations.'),
    'Quantum-gravity consistency of effective field theories': (
        'EFT consistency', 'Use the conventional effective-field-theory abbreviation; the original label retains the quantum-gravity scope.'),
    'De Sitter quantum gravity: horizons, observables and consistency': (
        'de Sitter quantum gravity', 'Retain the setting and subject; horizon, observable and consistency distinctions remain in the original label.'),
    'Black-hole and holographic entropy: origins and consistency': (
        'Black-hole & holographic entropy', 'Retain both entropy settings without asserting that their origins or consistency arguments coincide.'),
    'Holographic quantum gravity: boundary descriptions, information bounds and consistency': (
        'Holographic quantum gravity', 'Retain the shared subject; the original label preserves boundary-description and information-bound distinctions.'),
    'Euclidean wormholes: quantum consistency, couplings and cosmological saddles': (
        'Euclidean wormholes', 'Retain the explicit Euclidean setting; the original label preserves the different uses and consistency questions.'),
    'Black-hole extremality and entropy as tests of weak gravity': (
        'Extremality, entropy & weak gravity', 'Retain all three concepts; the original label supplies the black-hole setting and conditional test relationship.'),
    'Inflation and scalar dark-sector cosmology: observations and theoretical consistency': (
        'Inflation & scalar dark-sector cosmology', 'Retain the scalar qualifier and both cosmological subjects; the original label retains the observational and theoretical tests.'),
    'Neutrino mass origins and tests: symmetries, extra dimensions and quantum gravity': (
        'Neutrino mass: origins & tests', 'Retain the actual common question; the original label lists alternative symmetry, extra-dimensional and quantum-gravity settings.'),
    'Descriptions awaiting a better home': (
        'Awaiting a better home', 'Shorten the navigational label while preserving unresolved membership rather than calling these sources invalid or noise.'),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def read_pinned(path, expected):
    raw = path.read_bytes()
    require(sha(raw) == expected, f'SHA-256 mismatch: {path.name}')
    return raw, json.loads(raw)


def export(source_path, corpus_root):
    source_raw, source = read_pinned(source_path, SOURCE_SHA256)
    release_raw, release = read_pinned(source_path.parent / 'MANIFEST.json', RELEASE_SHA256)
    require(release['files']['map-data.json'] == {'bytes': len(source_raw), 'sha256': SOURCE_SHA256}, 'Release map pin differs')
    corpus_raw = (corpus_root / 'manifest.json').read_bytes()
    corpus = json.loads(corpus_raw)
    require(any(pin['path'] == SOURCE_PATH and pin['sha256'] == SOURCE_SHA256 for pin in corpus['inputs']), 'Source is not the frozen corpus input')
    view = next(view for view in source['views'] if view['id'] == VIEW_ID)
    units, original_topics = view['units'], view['topics']
    require(len(units) == 8473 and len(original_topics) == 12 and len(view['links']) == 42, 'Pinned question-view counts differ')
    require(set(CAPTIONS) == {topic['label'] for topic in original_topics}, 'Caption review does not match exact source labels')
    require(view['coverage']['scientific_relation_promotions'] == 0, 'Unexpected scientific relation promotion')
    require({unit['component'] for unit in units} == {0}, 'Single-component display assumption changed')

    current = {}
    for item in corpus['files']['units']:
        raw, shard = read_pinned(corpus_root / item['path'], item['sha256'])
        require(len(raw) == item['bytes'], 'Frozen unit shard size differs')
        for unit in shard:
            if unit['lens'] == 'physical_question':
                require(unit['id'] not in current, 'Duplicate current question ID')
                current[unit['id']] = unit
    require(set(current) == {unit['id'] for unit in units}, 'Question unit coverage differs from frozen corpus')

    topic_index = {topic['id']: i for i, topic in enumerate(original_topics)}
    unit_index = {unit['id']: i for i, unit in enumerate(units)}
    require(len(topic_index) == len(original_topics) and len(unit_index) == len(units), 'Duplicate source IDs')
    root_index = topic_index[view['root_id']]
    require(original_topics[root_index]['parent_id'] is None, 'Root has a parent')
    for topic in original_topics:
        seen, ancestor = set(), topic
        while ancestor is not None:
            require(ancestor['id'] not in seen, 'Hierarchy cycle')
            seen.add(ancestor['id'])
            parent_id = ancestor['parent_id']
            require(parent_id is None or parent_id in topic_index, 'Unknown parent')
            ancestor = original_topics[topic_index[parent_id]] if parent_id is not None else None
        require(view['root_id'] in seen, 'Disconnected topic')
        children = topic['children']
        require(len(set(children)) == len(children), 'Repeated child')
        require(all(child in topic_index and original_topics[topic_index[child]]['parent_id'] == topic['id'] for child in children), 'Inconsistent parent/children')
        if topic['parent_id'] is not None:
            require(topic['id'] in original_topics[topic_index[topic['parent_id']]]['children'], 'Parent omits child')

    paper_ids = {unit['paper_id'] for unit in units}
    source_papers = [paper for paper in source['papers'] if paper['id'] in paper_ids]
    require(len(source_papers) == len(paper_ids) == 6477, 'Paper catalog coverage differs')
    paper_index = {paper['id']: i for i, paper in enumerate(source_papers)}
    papers = []
    for paper in source_papers:
        url = urlsplit(paper['url'])
        require(url.scheme in ('http', 'https') and url.netloc and not url.username and not url.password, 'Unsafe paper URL')
        require(isinstance(paper['title'], str) and paper['title'].strip(), 'Missing source title')
        papers.append([paper['id'], paper['title'], paper['url']])

    points, texts = [], []
    topic_members = [set() for _ in original_topics]
    paper_mass = collections.defaultdict(float)
    overlap = internal_homes = 0
    for i, unit in enumerate(units):
        current_unit = current[unit['id']]
        require(unit['facet'] == current_unit['lens'] == 'physical_question', 'Unit lens mismatch')
        require(unit['paper_id'] == current_unit['paperId'], 'Unit paper mismatch')
        require(sha(unit['text'].encode('utf-8')) == unit['text_sha256'] == current_unit['evidence']['textSha256'], 'Exact source text hash differs')
        require(unit['text'] == current_unit['text'], 'Exact source text differs')
        require(unit['mass'] == current_unit['mass'] and unit['mass'] > 0, 'Source mass differs')
        require(all(math.isfinite(unit[key]) for key in ['x', 'y', 'mass']), 'Nonfinite coordinate or mass')
        homes = unit['topic_ids']
        require(homes and len(set(homes)) == len(homes) and set(homes) <= set(topic_index), 'Invalid direct homes')
        require(set(homes) == set(unit['topic_membership_weights']), 'Membership weight keys differ')
        require(all(unit['topic_membership_weights'][home] == unit['mass'] / len(homes) for home in homes), 'Unequal source weights cannot use compact encoding')
        overlap += len(homes) > 1
        internal_homes += any(original_topics[topic_index[home]]['children'] for home in homes)
        paper_mass[unit['paper_id']] += unit['mass']
        for home in homes:
            topic = original_topics[topic_index[home]]
            while topic is not None:
                topic_members[topic_index[topic['id']]].add(i)
                topic = original_topics[topic_index[topic['parent_id']]] if topic['parent_id'] is not None else None
        points.append([unit['id'], paper_index[unit['paper_id']], unit['x'], unit['y'], unit['mass'], [topic_index[home] for home in homes]])
        texts.append(unit['text'])
    require(overlap == 10 and internal_homes == 1, 'Overlap/internal-home coverage differs')
    require(max(abs(mass - 1) for mass in paper_mass.values()) < 1e-12, 'Paper mass conservation failed')

    topics = []
    for i, topic in enumerate(original_topics):
        members = topic_members[i]
        require(len(members) == topic['unit_count'], 'Topic unit count differs from actual membership')
        require(len({points[row][1] for row in members}) == topic['paper_count'], 'Topic paper count differs from actual membership')
        require(all(math.isfinite(topic[key]) for key in ['x', 'y', 'mass']), 'Nonfinite topic geometry')
        caption, rationale = CAPTIONS[topic['label']]
        topics.append({
            'id': topic['id'], 'label': topic['label'], 'caption': caption, 'captionRationale': rationale,
            'parent': topic_index[topic['parent_id']] if topic['parent_id'] is not None else None,
            'children': [topic_index[child] for child in topic['children']], 'depth': topic['depth'],
            'x': topic['x'], 'y': topic['y'], 'unitCount': topic['unit_count'], 'paperCount': topic['paper_count'],
            'mass': topic['mass'], 'status': topic['status'], 'summary': topic['summary'],
            'limitations': topic['limitations'], 'freshConcern': bool(topic.get('fresh_applicability', {}).get('concern')),
            'representatives': [unit_index[uid] for uid in topic['representative_unit_ids']],
        })
    unresolved = [i for i, topic in enumerate(topics) if topic['id'].endswith(':unresolved-memberships')]
    require(len(unresolved) == 1 and len(topic_members[unresolved[0]]) == 13, 'Unresolved coverage differs')
    require(topics[unresolved[0]]['status'] == 'deferred', 'Unresolved status differs')

    links, link_pairs = [], set()
    for link in view['links']:
        require(link['source'] in topic_index and link['target'] in topic_index, 'Unknown link endpoint')
        a, b = topic_index[link['source']], topic_index[link['target']]
        pair = tuple(sorted([a, b]))
        require(a != b and pair not in link_pairs and math.isfinite(link['weight']) and link['weight'] > 0, 'Invalid topic affinity')
        require(link['kind'] == 'text_similarity' and link['membership_basis'] == 'current_reviewed_memberships', 'Unexpected edge semantics')
        link_pairs.add(pair)
        links.append({'source': a, 'target': b, 'weight': link['weight'], 'kind': link['kind']})
    map_data = {'schemaVersion': '1.0.0', 'viewId': VIEW_ID, 'pointColumns': POINT_COLUMNS,
                'paperColumns': PAPER_COLUMNS, 'points': points, 'papers': papers, 'topics': topics, 'links': links}
    files = {'map.json': encode(map_data)}
    details = []
    for start in range(0, len(texts), SHARD_SIZE):
        shard = {'schemaVersion': '1.0.0', 'start': start, 'texts': texts[start:start + SHARD_SIZE]}
        path = f'details-{start // SHARD_SIZE:03d}.json'
        raw = encode(shard)
        files[path] = raw
        details.append({'path': path, 'sha256': sha(raw), 'bytes': len(raw), 'start': start, 'count': len(shard['texts'])})
    manifest = {
        'schemaVersion': '1.0.0', 'kind': 'eigenquestions-fixed-overview', 'viewId': VIEW_ID,
        'source': {'path': SOURCE_PATH, 'sha256': SOURCE_SHA256, 'bytes': len(source_raw),
                   'snapshotId': source['snapshot']['id'], 'releaseManifestSha256': sha(release_raw)},
        'corpusId': corpus['corpusId'], 'snapshotDate': corpus['snapshotDate'],
        'scope': {'collection': 'Swampland-centered frozen corpus',
                  'pointMeaning': 'source-scoped extracted physical-question description',
                  'paperCount': len(papers), 'facetCount': len(points),
                  'limitations': ['The collection does not cover all physics or all relevant literature.',
                                  'Dots are question descriptions; a paper may contribute multiple dots and occur in multiple topics.',
                                  'Topic labels and memberships are provisional organizational proposals with sampled agent review.',
                                  'The supplied hierarchy ends at depth two; zoom does not establish further scientific subdivisions.']},
        'counts': {'facets': len(points), 'papers': len(papers),
                   'topics': len(topics), 'links': len(links), 'overlapFacets': overlap,
                   'internalHomeFacets': internal_homes, 'unresolvedFacets': len(topic_members[unresolved[0]])},
        'rootTopicIndex': root_index, 'layout': view['layout'],
        'membershipRule': {'unitMass': '1 / descriptions from this paper in the question lens',
                           'directHomeWeight': 'unit mass / number of distinct direct homes',
                           'weightsAreProbabilities': False, 'ancestorMembership': 'union of direct homes and descendants; preserve internal direct homes',
                           'unresolvedTopicIndex': unresolved[0]},
        'linkRule': view['coarse_recomputation'],
        'files': {'map': {'path': 'map.json', 'sha256': sha(files['map.json']), 'bytes': len(files['map.json'])}, 'details': details},
        'exportAudit': {'builder': 'scripts/data/build-overview.py', 'builderSha256': sha(Path(__file__).read_bytes()),
                        'corpusManifestSha256': sha(corpus_raw), 'sourceUnitIdentityAndTextHashes': 'all 8473 match frozen corpus exactly',
                        'directHomeWeights': 'all original weights equal preserved mass / complete home count exactly',
                        'topicCounts': 'all exact source counts match membership-derived facet and distinct-paper counts',
                        'coordinatePolicy': 'exact supplied source float values; single component 0; no new layout or aggregation',
                        'captionPolicy': 'original labels retained; separate display caption and rationale; no scientific membership edits'},
    }
    files['manifest.json'] = encode(manifest)
    require(len(files['manifest.json']) + len(files['map.json']) < MAX_INITIAL_BYTES, 'Initial JSON exceeds 3 MB budget')
    require(len(details) == 17 and max(item['bytes'] for item in details) < 120_000, 'Detail-shard bounds differ')
    return files, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'data/overview')
    parser.add_argument('--check', action='store_true', help='Compare exact generated bytes without writing')
    args = parser.parse_args()
    files, manifest = export(args.source, ROOT / 'data/navigation')
    if args.check:
        require(args.output.exists(), 'Overview output is missing')
        require({path.name for path in args.output.iterdir() if path.is_file()} == set(files), 'Overview file inventory differs')
        for name, raw in files.items():
            require((args.output / name).read_bytes() == raw, f'Generated bytes differ: {name}')
    else:
        args.output.mkdir(parents=True, exist_ok=True)
        require(not ({path.name for path in args.output.iterdir()} - set(files)), 'Unexpected output files; refusing to remove them')
        for name, raw in files.items():
            (args.output / name).write_bytes(raw)
    print(json.dumps({'checked' if args.check else 'exported': True, 'sourceSha256': SOURCE_SHA256,
                      'viewId': VIEW_ID, 'counts': manifest['counts'], 'files': len(files),
                      'initialBytes': len(files['manifest.json']) + len(files['map.json']),
                      'mapBytes': len(files['map.json']), 'totalBytes': sum(map(len, files.values())),
                      'maximumDetailBytes': max(item['bytes'] for item in manifest['files']['details'])}, indent=2))


if __name__ == '__main__':
    main()
