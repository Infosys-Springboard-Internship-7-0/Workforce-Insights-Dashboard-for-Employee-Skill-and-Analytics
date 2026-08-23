import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User

email = input("Admin email: ").strip()
name = input("Admin name: ").strip()
password = input("Admin password: ")

db = SessionLocal()

try:
    existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing:
        print("Admin already exists.")
        raise SystemExit(0)

    db.add(User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="admin",
        is_active=True,
    ))
    db.commit()
    print("Admin created.")
finally:
    db.close()
