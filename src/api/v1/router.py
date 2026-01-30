# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from fastapi import APIRouter

from src.api.v1 import config_routes, evaluation, ingestion, reports, feedback, sales

api_router = APIRouter()

api_router.include_router(evaluation.router, tags=["evaluation"])
api_router.include_router(ingestion.router, tags=["ingestion"])
api_router.include_router(reports.router, tags=["reports"])
api_router.include_router(sales.router, tags=["sales"])
api_router.include_router(config_routes.router, tags=["config"])
api_router.include_router(feedback.router, prefix="/safety", tags=["safety"])
