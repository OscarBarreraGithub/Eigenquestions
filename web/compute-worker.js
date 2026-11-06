import { loadCorpus, createNavigator } from '/lib/geometry/index.mjs';
import { createSession, currentState, applyAction, importSession, validateSession } from '/lib/protocol/session.mjs';
let navigator, session;
self.onmessage = async ({ data: message }) => {
  const { id, type, payload } = message;
  try {
    let view;
    if (type === 'init') {
      const corpus = await loadCorpus('/data/', { onProgress: progress => self.postMessage({ type: 'progress', ...progress }) });
      self.postMessage({ type: 'progress', stage: 'index' });
      navigator = createNavigator(corpus);
      session = payload?.session ? importSession(payload.session, { corpusId: corpus.manifest.corpusId, computationId: navigator.computationId }) : createSession({ corpusId: corpus.manifest.corpusId, computationId: navigator.computationId, query: 'Kaluza-Klein towers', ...payload?.state });
      view = navigator.computeView(currentState(session));
      self.postMessage({ id, result: { session, view, manifest: corpus.manifest } });
      return;
    }
    if (!navigator) throw new Error('The corpus is still loading. Please wait before navigating.');
    if (type === 'action') ({ session, view } = applyAction(session, payload, navigator));
    else if (type === 'import') {
      session = payload.kind === 'eigenquestions-session'
        ? importSession(payload, { corpusId: session.corpusId, computationId: navigator.computationId })
        : validateSession(payload.session, { corpusId: session.corpusId, computationId: navigator.computationId });
      view = navigator.computeView(currentState(session));
    } else throw new Error(`Unknown browser operation: ${type}`);
    self.postMessage({ id, result: { session, view } });
  } catch (error) { self.postMessage({ id, error: error.message }); }
};
