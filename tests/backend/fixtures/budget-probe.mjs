// Test-only worker. This module is never a production entry point or public asset.
import {DurableObject} from 'cloudflare:workers';
import {BudgetLedger} from '../../../backend/budget.mjs';

export class TestBudget extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.time = '2026-11-06T12:00:00Z';
    this.ledger = new BudgetLedger(ctx.storage, JSON.parse(env.TEST_LIMITS), () => new Date(this.time));
  }
  reserve(digest, bytes, time) { if (time) this.time = time; return this.ledger.reserve(digest, bytes); }
  inspect() { return this.ctx.storage.sql.exec('SELECT * FROM budget').one(); }
}
export default {
  async fetch(request, env) {
    const budget = env.TEST_BUDGET.getByName('one-budget');
    if (request.method === 'GET') return Response.json(await budget.inspect());
    const {digest, bytes, time} = await request.json();
    return Response.json(await budget.reserve(digest, bytes, time));
  },
};
