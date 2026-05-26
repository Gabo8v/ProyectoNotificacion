import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database import engine, SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Check tables
    tables = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")).all()
    print("Tables:", [t[0] for t in tables])
    
    # Check notification count
    count = db.execute(text("SELECT COUNT(*) FROM notifications")).scalar()
    print(f"Notifications: {count}")
    
    # Check recent
    rows = db.execute(text("SELECT id, channel, status, subject, created_at FROM notifications ORDER BY created_at DESC LIMIT 10")).all()
    for r in rows:
        print(f"  {r.id}: {r.channel} | {r.subject[:30] if r.subject else '-'} | {r.status} | {r.created_at}")
except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()
finally:
    db.close()
