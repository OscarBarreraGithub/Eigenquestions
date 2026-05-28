// D1 Database types for Cloudflare Workers
// Declared manually to avoid @cloudflare/workers-types overriding global Response type

interface D1Database {
  prepare(query: string): D1PreparedStatement;
  exec(query: string): Promise<D1ExecResult>;
  batch<T = unknown>(statements: D1PreparedStatement[]): Promise<D1Result<T>[]>;
  dump(): Promise<ArrayBuffer>;
}

interface D1PreparedStatement {
  bind(...values: unknown[]): D1PreparedStatement;
  first<T = unknown>(colName?: string): Promise<T | null>;
  run<T = unknown>(): Promise<D1Result<T>>;
  all<T = unknown>(): Promise<D1Result<T>>;
  raw<T = unknown>(options?: { columnNames?: boolean }): Promise<T[]>;
}

interface D1Result<T = unknown> {
  results: T[];
  success: boolean;
  meta: D1Meta;
}

interface D1Meta {
  duration: number;
  last_row_id: number | null;
  changes: number | null;
  served_by: string;
  internal_stats: null;
  rows_read: number;
  rows_written: number;
}

interface D1ExecResult {
  count: number;
  duration: number;
}

interface CloudflareEnv {
  DB: D1Database;
}
