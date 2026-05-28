import { getDb } from "../src/lib/db";
import fs from "fs";
import path from "path";

function main() {
  const db = getDb();

  const row = db
    .prepare("SELECT COUNT(*) as count FROM questions")
    .get() as { count: number };

  if (row.count > 0) {
    console.log(
      `Database already has ${row.count} questions. Skipping seed.`
    );
    return;
  }

  const questionsPath = path.join(process.cwd(), "data", "questions.json");
  const questions: string[] = JSON.parse(
    fs.readFileSync(questionsPath, "utf-8")
  );

  const insert = db.prepare("INSERT INTO questions (text) VALUES (?)");

  const insertAll = db.transaction((items: string[]) => {
    for (const text of items) {
      insert.run(text);
    }
  });

  insertAll(questions);
  console.log(`Successfully seeded ${questions.length} questions.`);
}

main();
