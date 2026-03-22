from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import transactions, budgets, insights, actions
from app.database import init_db, seed_data
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_data()
    yield

app = FastAPI(
    title="Financial Service",
    description="Core financial logic, Insight Engine, and Intervention Engine for MoneyLane",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["Budgets"])
app.include_router(insights.router, prefix="/api/v1/insights", tags=["Insights"])
app.include_router(actions.router, prefix="/api/v1/actions", tags=["Actions"])


@app.get("/health")
async def health():
    return {"status": "ok"}
