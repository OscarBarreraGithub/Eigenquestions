/** Durable admission bookkeeping only; never stores or computes scientific views. */
export const BUDGET_NAME = 'public-view-budget-v1';
export const BUDGET_LIMITS = Object.freeze({bytes: 8_000_000_000, objects: 100_000, newPerDay: 2_000, attemptsPerDay: 8_000});
export const VIEW_ID = /^[A-Za-z0-9_-]{22}$/;

function randomId() {
  return btoa(String.fromCharCode(...crypto.getRandomValues(new Uint8Array(16)))).replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/, '');
}

export class BudgetLedger {
  constructor(storage, limits = BUDGET_LIMITS, now = () => new Date()) {
    this.storage = storage;
    this.limits = limits;
    this.now = now;
    storage.sql.exec(`CREATE TABLE IF NOT EXISTS budget (
      singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
      bytes INTEGER NOT NULL, objects INTEGER NOT NULL,
      day TEXT NOT NULL, new_today INTEGER NOT NULL, attempts_today INTEGER NOT NULL
    );
    INSERT OR IGNORE INTO budget VALUES (1, 0, 0, '', 0, 0);
    CREATE TABLE IF NOT EXISTS reservations (
      digest TEXT PRIMARY KEY, id TEXT NOT NULL UNIQUE, bytes INTEGER NOT NULL, created_at TEXT NOT NULL
    );`);
  }

  reserve(digest, bytes) {
    if (!/^[a-f0-9]{64}$/.test(digest) || !Number.isSafeInteger(bytes) || bytes < 1 || bytes > 512 * 1024) throw new Error('Invalid storage reservation');
    const time = this.now(), day = time.toISOString().slice(0, 10);
    const retryAfter = Math.max(1, Math.ceil((Date.parse(`${day}T00:00:00Z`) + 86_400_000 - time.getTime()) / 1000));
    return this.storage.transactionSync(() => {
      const sql = this.storage.sql;
      const state = sql.exec('SELECT * FROM budget WHERE singleton = 1').one();
      // Never move a persisted quota day backwards if an instance clock regresses.
      if (day > state.day) { state.day = day; state.new_today = 0; state.attempts_today = 0; }
      if (state.attempts_today >= this.limits.attemptsPerDay) return {ok: false, code: 'daily_attempt_limit', retryAfter};
      sql.exec('UPDATE budget SET day = ?, new_today = ?, attempts_today = ? WHERE singleton = 1', state.day, state.new_today, state.attempts_today + 1);
      const existing = sql.exec('SELECT * FROM reservations WHERE digest = ?', digest).toArray()[0];
      if (existing) {
        if (existing.bytes !== bytes) throw new Error('Digest reservation size mismatch');
        return {ok: true, id: existing.id, createdAt: existing.created_at, reused: true};
      }
      if (state.new_today >= this.limits.newPerDay) return {ok: false, code: 'daily_save_limit', retryAfter};
      if (state.bytes + bytes > this.limits.bytes || state.objects >= this.limits.objects) return {ok: false, code: 'storage_capacity', retryAfter: null};
      const id = randomId(), createdAt = time.toISOString();
      sql.exec('INSERT INTO reservations (digest, id, bytes, created_at) VALUES (?, ?, ?, ?)', digest, id, bytes, createdAt);
      sql.exec('UPDATE budget SET bytes = bytes + ?, objects = objects + 1, new_today = new_today + 1 WHERE singleton = 1', bytes);
      return {ok: true, id, createdAt, reused: false};
    });
  }
}
