"""Recommendation service facade."""
from __future__ import annotations
from src.recommendations.rule_engine import evaluate
def recommend(sample: dict) -> list[dict]: return evaluate(sample)
