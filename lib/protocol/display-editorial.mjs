/** Presentation-only annotations. The scientific record is never rewritten. */
const fail = message => { throw new Error(`Display editorial: ${message}`); };
const hash = value => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
const text = (value, name, limit = 8000) => {
  if (typeof value !== 'string' || !value.trim() || value.length > limit) fail(`invalid ${name}`);
};

/** An explicit recorded notice may distinguish placement gaps from missing context. */
export function validateSourceHomeNotice(record) {
  if (record.sourceHomeNotice === undefined) return;
  if (record.sourceHomeStatus !== 'unresolved') fail('source-home notice requires unresolved placement');
  text(record.sourceHomeNotice, 'source-home notice', 1000);
  text(record.sourceHomeReason, 'source-home reason');
}

export function validateDisplayEditorial(record) {
  const editorial = record.displayEditorial;
  if (editorial === undefined) return;
  if (!editorial || editorial.schemaVersion !== '1.0.0' || editorial.kind !== 'presentation-only') fail('unsupported annotation');
  if (!hash(editorial.scopeContentSha256) || editorial.scopeContentSha256 !== record.scopeContentSha256) fail('scientific scope binding changed');
  const origin = editorial.origin;
  if (!origin || !hash(origin.artifactSha256) || typeof origin.artifactPath !== 'string' || !/^[a-zA-Z0-9][a-zA-Z0-9._/-]*\.json$/.test(origin.artifactPath) || origin.artifactPath.split('/').includes('..') || !/^\/destinations\/\d+$/.test(origin.recordPointer || '')) fail('missing exact source-record origin');
  if (!Array.isArray(editorial.relocations) || editorial.relocations.length > 100) fail('invalid relocations');
  const seen = new Set();
  for (const note of editorial.relocations) {
    const match = /^\/scope\/(assumptions|conventions)\/(0|[1-9]\d*)$/.exec(note.path || '');
    if (!match || seen.has(note.path)) fail('invalid or duplicate field path');
    seen.add(note.path);
    if (!['workflow', 'reading'].includes(note.category)) fail('invalid note category');
    text(note.originalText, 'original text'); text(note.reason, 'editorial reason', 2000);
    if (record.scope?.[match[1]]?.[Number(match[2])] !== note.originalText) fail('original field text changed');
  }
  if (editorial.summary !== undefined) {
    text(editorial.summary.text, 'display summary'); text(editorial.summary.originalText, 'original summary'); text(editorial.summary.reason, 'summary reason', 2000);
    if (editorial.summary.originalText !== record.summary) fail('original summary changed');
  }
  if (editorial.readingLimit !== undefined) {
    const note = editorial.readingLimit;
    if (!['/readingLimit', '/readingCoverage/readingLimit'].includes(note.path)) fail('invalid reading-limit path');
    text(note.text, 'display reading limit'); text(note.originalText, 'original reading limit'); text(note.reason, 'reading-limit reason', 2000);
    if ((note.path === '/readingLimit' ? record.readingLimit : record.readingCoverage?.readingLimit) !== note.originalText) fail('original reading limit changed');
  }
}

export function destinationPresentation(record) {
  validateDisplayEditorial(record);
  validateSourceHomeNotice(record);
  const editorial = record.displayEditorial, scope = structuredClone(record.scope || {}), reading = [], coverage = record.readingCoverage;
  if (typeof record.readingLimit === 'string') reading.push(editorial?.readingLimit?.path === '/readingLimit' ? editorial.readingLimit.text : record.readingLimit);
  if (typeof coverage === 'string') reading.push(coverage);
  else if (coverage && typeof coverage === 'object') {
    const counts = [];
    if (Number.isSafeInteger(coverage.descriptionCheckedCount)) counts.push(`${coverage.descriptionCheckedCount} extracted descriptions checked`);
    if (Number.isSafeInteger(coverage.excerptCheckedCount)) counts.push(`${coverage.excerptCheckedCount} source excerpts checked`);
    if (counts.length) reading.push(counts.join('; ') + '.');
    if (typeof coverage.readingLimit === 'string') reading.push(editorial?.readingLimit?.path === '/readingCoverage/readingLimit' ? editorial.readingLimit.text : coverage.readingLimit);
  }
  const output = {summary: record.summary, scope, reading: [...new Set(reading)], readingRecord: typeof coverage === 'object' ? structuredClone(coverage) : null, notes: [], sourceHomeNotice: record.sourceHomeStatus === 'unresolved' ? record.sourceHomeNotice ?? 'More source context is needed for precise topic placement.' : null};
  if (!editorial) return output;
  const relocated = new Set(editorial.relocations.map(note => note.path));
  for (const field of ['assumptions', 'conventions']) if (scope[field]) scope[field] = scope[field].filter((_, index) => !relocated.has(`/scope/${field}/${index}`));
  const notes = editorial.relocations.map(note => ({...structuredClone(note), origin: structuredClone(editorial.origin)}));
  if (editorial.summary) notes.unshift({path: '/summary', category: 'workflow', originalText: editorial.summary.originalText, reason: editorial.summary.reason, origin: structuredClone(editorial.origin)});
  if (editorial.readingLimit) notes.push({...structuredClone(editorial.readingLimit), category: 'reading', origin: structuredClone(editorial.origin)});
  return {...output, summary: editorial.summary?.text ?? record.summary, notes, scopeContentSha256: editorial.scopeContentSha256};
}

/** Compact navigation uses the exact scoped question, not historical review prose.
 * This is a field selection, never a rewrite of scientific definitions. Full
 * descriptions, reading limits and explicit editorial notes remain in detail. */
export function destinationPreview(record) {
  return {summary: record.metadataOnly ? record.summary || '' : record.question ?? record.title ?? ''};
}
