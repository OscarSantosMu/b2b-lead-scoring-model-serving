"""
Lead scoring feature schema with 50 features for B2B lead scoring model.
Features cover company firmographics, engagement metrics, and behavioral signals.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Tier definitions mapping bucket to tier
TIER_DEFINITIONS = {
    "A": "Highest conversion likelihood (bucket 5)",
    "B": "High conversion likelihood (bucket 4)",
    "C": "Medium conversion likelihood (bucket 3)",
    "D": "Low conversion likelihood (bucket 2)",
    "E": "Lowest conversion likelihood (bucket 1)",
}


class LeadFeatures(BaseModel):
    """50-feature schema for B2B lead scoring."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                # Firmographics
                "company_revenue": 5000000,
                "company_employee_count": 250,
                "company_age_years": 8.5,
                "company_funding_total": 12000000,
                "company_growth_rate": 0.35,
                "industry_tech_score": 0.85,
                "geographic_tier": 1,
                "company_public_status": 0,
                "parent_company_exists": 1,
                "subsidiary_count": 3,
                # Engagement
                "website_visits_30d": 42,
                "page_views_30d": 156,
                "avg_session_duration_sec": 245.3,
                "bounce_rate": 0.32,
                "pricing_page_visits": 8,
                "demo_page_visits": 3,
                "documentation_views": 15,
                "email_open_rate": 0.68,
                "email_click_rate": 0.42,
                "emails_received": 12,
                "whitepaper_downloads": 2,
                "webinar_attendance": 1,
                "social_media_engagement": 8,
                "customer_success_interactions": 3,
                "support_ticket_count": 1,
                # Behavioral
                "days_since_first_touch": 45.0,
                "days_since_last_touch": 2.0,
                "total_touchpoints": 28,
                "multi_channel_engagement": 1,
                "decision_maker_contacted": 1,
                "champion_identified": 1,
                "budget_confirmed": 1,
                "timeline_confirmed": 1,
                "competitor_evaluation": 1,
                "technical_evaluation_started": 1,
                "contract_reviewed": 0,
                "security_questionnaire_completed": 1,
                "roi_calculator_used": 1,
                "custom_demo_requested": 1,
                "integration_questions_asked": 5,
                # Attribution
                "lead_source_quality": 0.9,
                "attribution_touchpoints": 8,
                "paid_channel_source": 1,
                "referral_source": 0,
                "event_source": 1,
                # Product Interest
                "product_tier_interest": 2,
                "feature_requests_count": 3,
                "use_case_alignment": 0.88,
                "integration_requirements": 4,
                "deployment_preference": 0,
            }
        }
    )

    # Company Firmographics (10 features)
    company_revenue: float = Field(..., ge=0, description="Annual company revenue in USD")
    company_employee_count: int = Field(..., ge=1, description="Number of employees")
    company_age_years: float = Field(..., ge=0, description="Company age in years")
    company_funding_total: float = Field(0.0, ge=0, description="Total funding raised in USD")
    company_growth_rate: float = Field(..., description="YoY revenue growth rate")
    industry_tech_score: float = Field(..., ge=0, le=1, description="Technology adoption score 0-1")
    geographic_tier: int = Field(..., ge=1, le=3, description="Geographic market tier 1-3")
    company_public_status: int = Field(..., ge=0, le=1, description="0=private, 1=public")
    parent_company_exists: int = Field(..., ge=0, le=1, description="Has parent company")
    subsidiary_count: int = Field(0, ge=0, description="Number of subsidiaries")

    # Engagement Metrics (15 features)
    website_visits_30d: int = Field(..., ge=0, description="Website visits last 30 days")
    page_views_30d: int = Field(..., ge=0, description="Total page views last 30 days")
    avg_session_duration_sec: float = Field(..., ge=0, description="Average session duration")
    bounce_rate: float = Field(..., ge=0, le=1, description="Website bounce rate")
    pricing_page_visits: int = Field(0, ge=0, description="Pricing page visits")
    demo_page_visits: int = Field(0, ge=0, description="Demo page visits")
    documentation_views: int = Field(0, ge=0, description="Documentation page views")
    email_open_rate: float = Field(0.0, ge=0, le=1, description="Email open rate")
    email_click_rate: float = Field(0.0, ge=0, le=1, description="Email click-through rate")
    emails_received: int = Field(0, ge=0, description="Total emails received")
    whitepaper_downloads: int = Field(0, ge=0, description="Whitepaper downloads")
    webinar_attendance: int = Field(0, ge=0, description="Webinars attended")
    social_media_engagement: int = Field(0, ge=0, description="Social media interactions")
    customer_success_interactions: int = Field(0, ge=0, description="CS interactions")
    support_ticket_count: int = Field(0, ge=0, description="Support tickets opened")

    # Behavioral Signals (15 features)
    days_since_first_touch: float = Field(..., ge=0, description="Days since first interaction")
    days_since_last_touch: float = Field(..., ge=0, description="Days since last interaction")
    total_touchpoints: int = Field(..., ge=1, description="Total interaction touchpoints")
    multi_channel_engagement: int = Field(..., ge=0, le=1, description="Engaged on 3+ channels")
    decision_maker_contacted: int = Field(..., ge=0, le=1, description="Decision maker reached")
    champion_identified: int = Field(0, ge=0, le=1, description="Internal champion identified")
    budget_confirmed: int = Field(0, ge=0, le=1, description="Budget confirmed")
    timeline_confirmed: int = Field(0, ge=0, le=1, description="Purchase timeline confirmed")
    competitor_evaluation: int = Field(0, ge=0, le=1, description="Evaluating competitors")
    technical_evaluation_started: int = Field(
        0, ge=0, le=1, description="Technical eval in progress"
    )
    contract_reviewed: int = Field(0, ge=0, le=1, description="Contract/MSA reviewed")
    security_questionnaire_completed: int = Field(0, ge=0, le=1, description="Security review done")
    roi_calculator_used: int = Field(0, ge=0, le=1, description="Used ROI calculator")
    custom_demo_requested: int = Field(0, ge=0, le=1, description="Requested custom demo")
    integration_questions_asked: int = Field(0, ge=0, description="Integration inquiries")

    # Lead Source & Attribution (5 features)
    lead_source_quality: float = Field(..., ge=0, le=1, description="Lead source quality score")
    attribution_touchpoints: int = Field(..., ge=1, description="Marketing attribution points")
    paid_channel_source: int = Field(..., ge=0, le=1, description="From paid channel")
    referral_source: int = Field(0, ge=0, le=1, description="From referral")
    event_source: int = Field(0, ge=0, le=1, description="From event/conference")

    # Product Interest Signals (5 features)
    product_tier_interest: int = Field(..., ge=1, le=3, description="Product tier interested in")
    feature_requests_count: int = Field(0, ge=0, description="Feature requests made")
    use_case_alignment: float = Field(..., ge=0, le=1, description="Use case fit score")
    integration_requirements: int = Field(0, ge=0, description="Required integrations")
    deployment_preference: int = Field(..., ge=0, le=2, description="0=cloud, 1=hybrid, 2=on-prem")

    @field_validator("bounce_rate", "email_open_rate", "email_click_rate")
    @classmethod
    def validate_rate(cls, v):
        """Ensure rates are valid percentages."""
        if not 0 <= v <= 1:
            raise ValueError("Rate must be between 0 and 1")
        return v


class ScoringRequest(BaseModel):
    """Request schema for lead scoring."""

    lead_id: str = Field(..., description="Unique lead identifier")
    features: LeadFeatures


class ModelInfo(BaseModel):
    """Model information in response."""

    name: str = Field(..., description="Model name")
    version: str = Field(..., description="Model version")


class TimingInfo(BaseModel):
    """Timing information for the request."""

    latency_ms: float = Field(..., description="Request latency in milliseconds")


class RankingInfo(BaseModel):
    """Ranking/tier definitions."""

    tier_definition: dict[str, str] = Field(
        default_factory=lambda: TIER_DEFINITIONS.copy(),
        description="Tier definitions mapping",
    )


class ScoreInfo(BaseModel):
    """Score information in response."""

    raw_score: float = Field(..., ge=0, le=1, description="Raw probability score [0, 1]")
    bucket: int = Field(..., ge=1, le=5, description="Score bucket 1-5")
    tier: str = Field(..., description="Tier A-E based on bucket")
    ranking: RankingInfo | None = Field(None, description="Tier ranking definitions")

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v):
        """Ensure tier is valid."""
        if v not in ["A", "B", "C", "D", "E"]:
            raise ValueError("Tier must be A, B, C, D, or E")
        return v


class ScoringResponse(BaseModel):
    """Response schema for lead scoring."""

    request_id: str = Field(..., description="Unique request identifier")
    model: ModelInfo = Field(..., description="Model information")
    lead_id: str = Field(..., description="Lead identifier")
    score: ScoreInfo = Field(..., description="Score details")
    timing: TimingInfo | None = Field(None, description="Timing information")
    api_version: str | None = Field(None, description="API version")
