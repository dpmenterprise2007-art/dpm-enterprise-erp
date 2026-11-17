import argparse
import getpass

from sqlalchemy import select

from app.db import SessionLocal
from app.models import User
from app.security import hash_password


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the first DPM ERP administrator.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    password = getpass.getpass("Set administrator password (minimum 12 characters): ")
    if len(password) < 12:
        raise SystemExit("Password must contain at least 12 characters.")
    with SessionLocal() as db:
        email = args.email.strip().lower()
        existing = db.scalar(select(User).where(User.email == email))
        if existing:
            raise SystemExit("A user with this email already exists.")
        db.add(User(email=email, full_name=args.name.strip(), password_hash=hash_password(password), role="admin"))
        db.commit()
    print(f"Administrator created: {email}")


if __name__ == "__main__":
    main()
