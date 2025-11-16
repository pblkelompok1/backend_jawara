import sys
sys.path.append('src')

from database.core import Base, engine
from entities.user import User
from entities.refresh_session import RefreshSession

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("✓ All tables created successfully!")

# Verify tables
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"\nTables in database: {tables}")
