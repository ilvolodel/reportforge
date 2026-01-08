"""Database initialization script - creates tables."""
import sys
from sqlalchemy import text
from .database import engine, Base, SessionLocal

# Import all models so they're registered with Base
from .models.user import User, MagicLink, Session
from .models.project import Project, TeamMember, Client
from .models.subscription import Subscription, Revenue
from .models.report import ReportVersion


def init_database():
    """Initialize database: create all tables."""
    print("🔧 Initializing ReportForge database...")

    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")

        # Create all tables
        print("📋 Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")

        # Display summary
        db = SessionLocal()
        try:
            print("\n📊 Database Summary:")
            user_count = db.query(User).count()
            project_count = db.query(Project).count()
            print(f"   Users: {user_count}")
            print(f"   Projects: {project_count}")
        finally:
            db.close()

        print("\n✅ Database initialization complete!")
        return True

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def reset_database():
    """Drop all tables and recreate (DANGEROUS - use only in development)."""
    print("⚠️  WARNING: Dropping all ReportForge tables...")
    response = input("Type 'YES' to confirm: ")
    if response != 'YES':
        print("❌ Aborted")
        return False

    print("🗑️  Dropping tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tables dropped")

    return init_database()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_database()
    else:
        init_database()
