"""
Insight routes — now includes predictions endpoint.
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.schemas import InsightResponse, PredictionResponse
from app.database import get_session
from app.engine.overspending import detect_overspending
from app.engine.waste import detect_waste
from app.engine.behavior import detect_behavior
from app.engine.ranking import rank_insights
from app.engine.predictor import predict_all
from typing import List

router = APIRouter()


@router.get("/home", response_model=InsightResponse)
async def get_home_insight(session: Session = Depends(get_session)):
    """Top-ranked insight for the home screen."""
    all_insights = []
    all_insights.extend(detect_overspending(session))
    all_insights.extend(detect_waste(session))
    all_insights.extend(detect_behavior(session))

    return rank_insights(all_insights)


@router.get("/predictions", response_model=List[PredictionResponse])
async def get_predictions(session: Session = Depends(get_session)):
    """
    Overspend predictions for all budgeted categories.
    Returns only categories where overspending is projected.
    """
    return predict_all(session)
