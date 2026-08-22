import getpass
import sys

from core.security import hash_password
from database import Base, SessionLocal, engine
from users.models import User, UserRole

Base.metadata.create_all(bind=engine)


def main():
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if existing_admin:
            print(f"An admin account already exists: {existing_admin.email}")
            sys.exit(1)

        email = input("Admin email: ").strip()
        if db.query(User).filter(User.email == email).first():
            print(f"{email} is already registered as a non-admin user.")
            sys.exit(1)

        password = getpass.getpass("Admin password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords did not match.")
            sys.exit(1)
        if len(password) < 8:
            print("Password must be at least 8 characters.")
            sys.exit(1)

        admin = User(
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
            is_verified=True,
        )
        db.add(admin)
        db.commit()
        print(f"Admin account created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
