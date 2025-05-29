# sql_engine.py

import json
from backend.app.core.memory.sql_model import MemoryRecord, SessionLocal

class SQLMemoryEngine:
    def save(self, user, key, value):
        val = json.dumps(value) if not isinstance(value, str) else value
        with SessionLocal() as db:
            rec = db.query(MemoryRecord).filter_by(user=user, key=key).first()
            if rec:
                rec.value = val
            else:
                rec = MemoryRecord(user=user, key=key, value=val)
                db.add(rec)
            db.commit()

    def fetch(self, user, key):
        with SessionLocal() as db:
            rec = db.query(MemoryRecord).filter_by(user=user, key=key).first()
            if rec and rec.value:
                try:
                    return json.loads(rec.value)
                except Exception:
                    return rec.value
            return None

    def clear(self, user):
        with SessionLocal() as db:
            db.query(MemoryRecord).filter_by(user=user).delete()
            db.commit()
