#!/usr/bin/env python3
"""
Seed script to create initial users in the database.
Run after starting the services to create default admin user.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.models.user import User


def seed_users():
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "merma_db")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")

    db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        existing_admin = db.query(User).filter(User.username == "admin").first()
        
        if existing_admin:
            print("Admin user already exists.")
            return
        
        admin_user = User(
            username="admin",
            password_hash=get_password_hash("admin123"),
            email="admin@merma.local",
            full_name="Administrator",
            is_active=True,
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Admin user created successfully! (ID: {admin_user.id})")
        print("  Username: admin")
        print("  Password: admin123")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()