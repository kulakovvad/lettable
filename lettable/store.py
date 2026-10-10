"""Local prototype persistence. One active request per authenticated conversation."""
import hashlib
import json
import sqlite3
import time
from contextlib import contextmanager


class Store:
    def __init__(self, path: str):
        self.path = path
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                  scope TEXT, request_id TEXT, fingerprint TEXT, status TEXT,
                  outcome TEXT, state TEXT, budget TEXT, updated REAL,
                  PRIMARY KEY(scope, request_id));
                CREATE TABLE IF NOT EXISTS conversations (
                  scope TEXT PRIMARY KEY, history TEXT NOT NULL);
                CREATE UNIQUE INDEX IF NOT EXISTS active_conversation ON runs(scope)
                  WHERE status IN ('running', 'awaiting_approval');
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def scope(principal: str, conversation: str) -> str:
        if not principal.strip() or not conversation.strip():
            raise ValueError("Authenticated principal and conversation are required")
        return hashlib.sha256(json.dumps([principal, conversation]).encode()).hexdigest()

    def claim(self, scope, request_id, message):
        fingerprint = hashlib.sha256(message.encode()).hexdigest()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM runs WHERE scope=? AND request_id=?", (scope, request_id)).fetchone()
            if row:
                if row["fingerprint"] != fingerprint:
                    raise ValueError("request_id already used for different input")
                return dict(row)
            try:
                db.execute("INSERT INTO runs VALUES (?,?,?,'running',NULL,NULL,'{}',?)",
                           (scope, request_id, fingerprint, time.time()))
            except sqlite3.IntegrityError as exc:
                raise ValueError("Conversation already has an active request") from exc
        return None

    def load(self, scope, request_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM runs WHERE scope=? AND request_id=?", (scope, request_id)).fetchone()
            if not row:
                raise ValueError("Unknown request for this principal and conversation")
            return dict(row)

    def claim_resume(self, scope, request_id):
        with self.connect() as db:
            cursor = db.execute("UPDATE runs SET status='running' WHERE scope=? AND request_id=? AND status='awaiting_approval'", (scope, request_id))
            if cursor.rowcount != 1:
                raise ValueError("Request is not awaiting approval, or is already being resumed")

    def history(self, scope):
        with self.connect() as db:
            row = db.execute("SELECT history FROM conversations WHERE scope=?", (scope,)).fetchone()
            return json.loads(row[0]) if row else []

    def save_budget(self, scope, request_id, budget):
        with self.connect() as db:
            db.execute("UPDATE runs SET budget=? WHERE scope=? AND request_id=?", (json.dumps(budget), scope, request_id))

    def finish(self, scope, request_id, outcome, state=None, history=None):
        with self.connect() as db:
            db.execute("UPDATE runs SET status=?,outcome=?,state=?,updated=? WHERE scope=? AND request_id=?",
                       (outcome.status, outcome.model_dump_json(), json.dumps(state) if state else None,
                        time.time(), scope, request_id))
            if history is not None:
                db.execute("INSERT INTO conversations VALUES (?,?) ON CONFLICT(scope) DO UPDATE SET history=excluded.history", (scope, json.dumps(history)))
