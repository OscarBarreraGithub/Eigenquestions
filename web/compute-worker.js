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
      const engine = createNavigator(corpus), viewCache = new Map();
      navigator = { ...engine, computeView(state) {
        if (viewCache.has(state.id)) return viewCache.get(state.id);
        const computed = engine.computeView(state);
        viewCache.set(state.id, computed);
        while (viewCache.size > 24) viewCache.delete(viewCache.keys().next().value);
        return computed;
      } };
      session = payload?.session ? importSession(payload.session, { corpusId: corpus.manifest.corpusId, computationId: navigator.computationId }) : createSession({ corpusId: corpus.manifest.corpusId, computationId: navigator.computationId, query: '', ...payload?.state });
      view = navigator.computeView(currentState(session));
      self.postMessage({ id, result: { session, view, manifest: corpus.manifest } });
      return;
    }
    if (!navigator) throw new Error('The corpus is still loading. Please wait before navigating.');
    if (type === 'orient') {
      const orientation = createSession({...payload, corpusId: session.corpusId, computationId: navigator.computationId});
      self.postMessage({id, result: {session: orientation, view: navigator.computeView(currentState(orientation))}});
      return;
    }
    if (type === 'evidence') {
      if (!Array.isArray(payload.ids) || payload.ids.length > 100) throw new Error('Supply at most 100 evidence IDs');
      self.postMessage({id, result: navigator.getEvidence(payload.ids)});
      return;
    }
    if (type === 'action') {
      // Each UI intent is rooted in the last visibly accepted session. A newer
      // search therefore never inherits an unseen, superseded worker result.
      const base = payload.baseSession ? validateSession(payload.baseSession, { corpusId: session.corpusId, computationId: navigator.computationId }) : session;
      ({ session, view } = applyAction(base, payload.action, navigator));
    }
    else if (type === 'import') {
      session = payload.kind === 'eigenquestions-session'
        ? importSession(payload, { corpusId: session.corpusId, computationId: navigator.computationId })
        : validateSession(payload.session, { corpusId: session.corpusId, computationId: navigator.computationId });
      view = navigator.computeView(currentState(session));
    } else throw new Error(`Unknown browser operation: ${type}`);
    self.postMessage({ id, result: { session, view } });
  } catch (error) { self.postMessage({ id, error: error.message }); }
};
