import {DurableObject} from 'cloudflare:workers';
import {BudgetLedger} from './budget.mjs';

/** One coordination atom for this bucket's finite upload budget, never for reads. */
export class ViewBudget extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.ledger = new BudgetLedger(ctx.storage);
  }
  reserve(digest, bytes) { return this.ledger.reserve(digest, bytes); }
}
