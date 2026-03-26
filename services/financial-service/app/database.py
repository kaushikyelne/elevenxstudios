import os
import logging
from sqlmodel import create_engine, SQLModel, Session, select
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/moneylane")

# For Cloud Run compatibility, strip +asyncpg or other async drivers if present
# since we are using psycopg2 (sync)
if "asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    logger.info("Normalized asyncpg DATABASE_URL for psycopg2")

# Log connection attempt (masking password)
masked_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
logger.info(f"Connecting to database at: {masked_url}")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def seed_data():
    from app.models import CategoryRule
    with Session(engine) as session:
        # Check if rules already exist
        if session.exec(select(CategoryRule)).first():
            return
            
        rules = [
            CategoryRule(keyword="swiggy", category="Food"),
            CategoryRule(keyword="zomato", category="Food"),
            CategoryRule(keyword="uber", category="Transport"),
            CategoryRule(keyword="ola", category="Transport"),
            CategoryRule(keyword="netflix", category="Entertainment"),
            CategoryRule(keyword="spotify", category="Entertainment"),
            CategoryRule(keyword="amazon", category="Shopping"),
        ]
        session.add_all(rules)
        session.commit()
