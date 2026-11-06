export function authoredCapsule(question = 'Can a tower decay into dark matter?') {
  return {
    schemaVersion: '1.0.0', kind: 'eigenquestions-contextual-view',
    builder: {id: 'an-independent-agent', version: 'research-7'},
    context: {question, assumptions: ['This is an authored reading map.'], history: [{question: 'A different route'}]},
    snapshot: {view: {
      stateId: 'authored-state', computationId: 'an-unavailable-future-engine', corpusId: 'pinned-corpus',
      nodes: [
        {id: 'source-one', title: 'First source', evidence: {text: 'Evidence one', url: 'https://arxiv.org/abs/2209.09249'}},
        {id: 'source-two', title: 'Second source', evidence: {text: 'Evidence two'}},
      ],
      directions: [
        {id: 'group-a', label: 'Agent label α', memberIds: ['source-two', 'source-one'], evidenceIds: ['source-one'], description: 'Authored scientific meaning'},
        {id: 'group-b', label: 'Overlapping group', memberIds: ['source-one'], evidenceIds: ['source-one']},
      ],
      edges: [{source: 'group-a', target: 'source-two', type: 'agent-hypothesis', evidence: 'A stated assumption, not a theorem'}],
      warnings: ['This is a hypothesis.'], diagnostics: {}, chart: null,
    }},
    continuation: {mode: 'snapshot-only', originStateId: 'authored-state', description: 'Read the authored snapshot; its builder is not installed.', actions: []},
  };
}
