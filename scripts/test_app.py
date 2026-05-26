import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test health
r = client.get("/health")
print("Health:", r.status_code, r.json())

# Test dashboard
r = client.get("/dashboard/")
print("Dashboard:", r.status_code)
if r.status_code != 200:
    # Look for the actual error in templates
    import traceback
    from app.database import SessionLocal
    from sqlalchemy.orm import joinedload
    from app.models.notification import Notification
    from app.models.user import User

    db = SessionLocal()
    try:
        total = db.query(Notification).count()
        print(f"Total notifications: {total}")
        latest = db.query(Notification).options(joinedload(Notification.user)).order_by(Notification.created_at.desc()).limit(5).all()
        for n in latest:
            print(f"  {n.id}: user={n.user_id}, user_obj={n.user}, subject={n.subject}, status={n.status}")
        users = db.query(User).all()
        print(f"Users: {len(users)}")
        for u in users:
            print(f"  {u.id}: {u.name}")
    except Exception as e:
        print(f"DB Error: {e}")
        traceback.print_exc()
    finally:
        db.close()
