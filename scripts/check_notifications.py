import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database import SessionLocal
from app.models.notification import Notification
from app.models.user import User
from datetime import datetime

db = SessionLocal()
try:
    # Recent notifications
    notifications = db.query(Notification).order_by(Notification.created_at.desc()).limit(10).all()
    print("=== RECENT NOTIFICATIONS ===")
    for n in notifications:
        user_name = db.query(User).filter(User.id == n.user_id).first()
        uname = user_name.name if user_name else "?"
        print(f"  [{n.created_at}] {n.channel.value} → {uname} | {n.subject[:30] if n.subject else '-'} | status={n.status.value} | error={n.error_message[:50] if n.error_message else '-'}")
    
    # Any pending ones
    pending = db.query(Notification).filter(Notification.status == 'pending').count()
    print(f"\nPending notifications: {pending}")
    
    # Check if WhatsApp bot status - look at recent failed ones
    failed = db.query(Notification).filter(Notification.status == 'failed').order_by(Notification.created_at.desc()).limit(5).all()
    if failed:
        print("\n=== RECENT FAILED ===")
        for n in failed:
            print(f"  [{n.created_at}] {n.channel.value} | error={n.error_message[:80] if n.error_message else '?'}")
finally:
    db.close()
