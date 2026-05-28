CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text TEXT NOT NULL,
  elo_rating REAL NOT NULL DEFAULT 1500.0,
  times_shown INTEGER NOT NULL DEFAULT 0,
  times_won INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS votes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  winner_id INTEGER NOT NULL REFERENCES questions(id),
  loser_id INTEGER NOT NULL REFERENCES questions(id),
  winner_elo_before REAL NOT NULL,
  loser_elo_before REAL NOT NULL,
  winner_elo_after REAL NOT NULL,
  loser_elo_after REAL NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_questions_elo ON questions(elo_rating DESC);
CREATE INDEX IF NOT EXISTS idx_votes_created ON votes(created_at);
CREATE INDEX IF NOT EXISTS idx_votes_winner ON votes(winner_id);
CREATE INDEX IF NOT EXISTS idx_votes_loser ON votes(loser_id);

CREATE TABLE IF NOT EXISTS submissions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  submitted_at TEXT NOT NULL DEFAULT (datetime('now')),
  reviewed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);

INSERT INTO questions (text) VALUES ('Electroweak sphalerons and baryon-number violation');
INSERT INTO questions (text) VALUES ('Collider probes of nonperturbative electroweak physics');
INSERT INTO questions (text) VALUES ('Field-theoretic descriptions of neural network complexity');
INSERT INTO questions (text) VALUES ('Flavor phenomenology in Randall-Sundrum models');
INSERT INTO questions (text) VALUES ('AI-assisted theoretical model building');
INSERT INTO questions (text) VALUES ('Classical algorithms for automated symbolic physics');
INSERT INTO questions (text) VALUES ('Exact saddles in quantum path integrals');
INSERT INTO questions (text) VALUES ('Picard-Lefschetz thimbles in quantum field theory');
INSERT INTO questions (text) VALUES ('Deeper understanding of the dilute instanton gas');
INSERT INTO questions (text) VALUES ('AI-assisted precision calculations in collider physics');
