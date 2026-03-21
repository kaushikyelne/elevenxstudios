import os
from sqlmodel import create_engine, SQLModel, Session, select
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/moneylane")

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
