# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from fastapi_limiter.depends import RateLimiter
from src.api.deps import get_api_key
from src.agents.prospector import ProspectingScout
from src.core.reporting import AuditReportGenerator
from src.schemas.agents import ProspectProfile

router = APIRouter()


@router.post(
    "/sales/prospect", 
    dependencies=[Depends(get_api_key), Depends(RateLimiter(times=10, seconds=60))],
    response_model=ProspectProfile
)
async def generate_sales_prospect(
    company_name: str, 
    target_role: str, 
    team_size: int, 
    industry: str = "generic"
):
    """
    SALES AGENT: Automates the creation of a 'Perfect Prospect' profile.
    Generates industry-specific drift scenarios to wow the customer during demos.
    """
    scout = ProspectingScout()
    return await scout.generate_profile(
        company_name=company_name, 
        target_role=target_role, 
        team_size=team_size, 
        industry=industry
    )


@router.get(
    "/sales/roi-calculator", 
    dependencies=[Depends(get_api_key), Depends(RateLimiter(times=20, seconds=60))]
)
async def calculate_roi(team_size: int, avg_salary: float = 150000.0, currency: str = "USD"):
    """
    SALES INTELLIGENCE: Interactive ROI Calculator.
    Now supports basic currency formatting (USD/EUR/GBP).
    """
    
    
    profile = ProspectProfile(
        company_name="ROI Calc",
        target_role="User",
        team_size=team_size,
        avg_developer_salary=avg_salary
    )
    
    # Delegate all math and conversion to the Core Engine
    roi = AuditReportGenerator.predict_roi(profile, currency=currency)
    
    symbol = "$" if currency == "USD" else "€" if currency == "EUR" else "£" if currency == "GBP" else currency
    
    return {
        "currency": currency,
        "efficiency_gain": f"{roi.slippage_reduction_percent}%",
        "recovered_hours_annual": f"{roi.developer_hours_recovered:,.0f}h",
        "annual_savings": f"{symbol}{roi.annual_savings_usd:,.2f}",
        "payback_period": f"{roi.payback_period_months} months",
        "message": roi.calculation_basis
    }


@router.post(
    "/sales/executive-brief", 
    dependencies=[Depends(get_api_key), Depends(RateLimiter(times=5, seconds=60))],
    response_class=HTMLResponse
)
async def generate_executive_brief(
    company_name: str, 
    target_role: str, 
    team_size: int, 
    industry: str,
    currency: str = "USD"
):
    """
    SALES ENABLEMENT: Generates a premium HTML one-pager for C-Level meetings.
    Combines Prospecting Scenarios + ROI Analysis.
    """
    
    # 1. Generate Profile & Scenarios
    scout = ProspectingScout()
    profile = await scout.generate_profile(company_name, target_role, team_size, industry)
    
    # 2. Calculate ROI
    roi = AuditReportGenerator.predict_roi(profile, currency=currency)
    
    # 3. Render HTML
    return AuditReportGenerator.generate_sales_brief_html(profile, roi, currency)
@router.get("/landing", response_class=HTMLResponse)
async def get_interactive_landing():
    """
    SALES INTERFACE: Serves the high-converting glassmorphic landing page.
    This is the entry point for custom 'Instant Demos'.
    """
    return HTMLResponse(content=AuditReportGenerator.render_landing_page())
