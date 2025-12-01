from sqlalchemy import create_engine, inspect
from app.config import settings
import os
import sys

sys.path.append(os.getcwd())

print(f"Checking DB: {settings.DATABASE_URL}")
engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
print("Tables:", inspector.get_table_names())
