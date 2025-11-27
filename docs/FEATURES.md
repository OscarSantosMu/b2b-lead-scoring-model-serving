# Feature Schema Documentation

## Overview

The B2B Lead Scoring model uses 50 features across 5 categories to predict lead conversion probability. All features are required for scoring.

## Table of Contents

- [Feature Categories](#feature-categories)
- [Score Output](#score-output)
- [Feature Engineering Tips](#feature-engineering-tips)
- [Validation Rules](#validation-rules)
- [API Integration](#api-integration)

## Feature Categories

### 1. Company Firmographics (10 features)

Information about the company size, maturity, and market position.

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `company_revenue` | float | [0, ∞) | Annual company revenue in USD |
| `company_employee_count` | int | [1, ∞) | Number of employees |
| `company_age_years` | float | [0, ∞) | Company age in years |
| `company_funding_total` | float | [0, ∞) | Total funding raised in USD |
| `company_growth_rate` | float | (-∞, ∞) | YoY revenue growth rate |
| `industry_tech_score` | float | [0, 1] | Technology adoption score |
| `geographic_tier` | int | [1, 3] | Geographic market tier (1=tier1, 3=tier3) |
| `company_public_status` | int | [0, 1] | 0=private, 1=public |
| `parent_company_exists` | int | [0, 1] | Has parent company |
| `subsidiary_count` | int | [0, ∞) | Number of subsidiaries |

**Example:**
```json
{
  "company_revenue": 5000000.0,
  "company_employee_count": 50,
  "company_age_years": 5.5,
  "company_funding_total": 2000000.0,
  "company_growth_rate": 0.35,
  "industry_tech_score": 0.8,
  "geographic_tier": 1,
  "company_public_status": 0,
  "parent_company_exists": 1,
  "subsidiary_count": 2
}
```

### 2. Engagement Metrics (15 features)

Digital engagement and interaction data over the past 30 days.

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `website_visits_30d` | int | [0, ∞) | Website visits last 30 days |
| `page_views_30d` | int | [0, ∞) | Total page views last 30 days |
| `avg_session_duration_sec` | float | [0, ∞) | Average session duration in seconds |
| `bounce_rate` | float | [0, 1] | Website bounce rate |
| `pricing_page_visits` | int | [0, ∞) | Pricing page visits |
| `demo_page_visits` | int | [0, ∞) | Demo page visits |
| `documentation_views` | int | [0, ∞) | Documentation page views |
| `email_open_rate` | float | [0, 1] | Email open rate |
| `email_click_rate` | float | [0, 1] | Email click-through rate |
| `emails_received` | int | [0, ∞) | Total emails received |
| `whitepaper_downloads` | int | [0, ∞) | Whitepaper downloads |
| `webinar_attendance` | int | [0, ∞) | Webinars attended |
| `social_media_engagement` | int | [0, ∞) | Social media interactions |
| `customer_success_interactions` | int | [0, ∞) | Customer success interactions |
| `support_ticket_count` | int | [0, ∞) | Support tickets opened |

**Example:**
```json
{
  "website_visits_30d": 45,
  "page_views_30d": 120,
  "avg_session_duration_sec": 180.5,
  "bounce_rate": 0.35,
  "pricing_page_visits": 5,
  "demo_page_visits": 3,
  "documentation_views": 10,
  "email_open_rate": 0.65,
  "email_click_rate": 0.25,
  "emails_received": 8,
  "whitepaper_downloads": 2,
  "webinar_attendance": 1,
  "social_media_engagement": 15,
  "customer_success_interactions": 2,
  "support_ticket_count": 0
}
```

### 3. Behavioral Signals (15 features)

Sales process progression and buying intent indicators.

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `days_since_first_touch` | float | [0, ∞) | Days since first interaction |
| `days_since_last_touch` | float | [0, ∞) | Days since last interaction |
| `total_touchpoints` | int | [1, ∞) | Total interaction touchpoints |
| `multi_channel_engagement` | int | [0, 1] | Engaged on 3+ channels |
| `decision_maker_contacted` | int | [0, 1] | Decision maker reached |
| `champion_identified` | int | [0, 1] | Internal champion identified |
| `budget_confirmed` | int | [0, 1] | Budget confirmed |
| `timeline_confirmed` | int | [0, 1] | Purchase timeline confirmed |
| `competitor_evaluation` | int | [0, 1] | Evaluating competitors |
| `technical_evaluation_started` | int | [0, 1] | Technical eval in progress |
| `contract_reviewed` | int | [0, 1] | Contract/MSA reviewed |
| `security_questionnaire_completed` | int | [0, 1] | Security review done |
| `roi_calculator_used` | int | [0, 1] | Used ROI calculator |
| `custom_demo_requested` | int | [0, 1] | Requested custom demo |
| `integration_questions_asked` | int | [0, ∞) | Integration inquiries |

**Example:**
```json
{
  "days_since_first_touch": 30.0,
  "days_since_last_touch": 2.0,
  "total_touchpoints": 25,
  "multi_channel_engagement": 1,
  "decision_maker_contacted": 1,
  "champion_identified": 1,
  "budget_confirmed": 0,
  "timeline_confirmed": 1,
  "competitor_evaluation": 1,
  "technical_evaluation_started": 1,
  "contract_reviewed": 0,
  "security_questionnaire_completed": 0,
  "roi_calculator_used": 1,
  "custom_demo_requested": 1,
  "integration_questions_asked": 3
}
```

### 4. Lead Source & Attribution (5 features)

Marketing source and channel attribution data.

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `lead_source_quality` | float | [0, 1] | Lead source quality score |
| `attribution_touchpoints` | int | [1, ∞) | Marketing attribution points |
| `paid_channel_source` | int | [0, 1] | From paid channel |
| `referral_source` | int | [0, 1] | From referral |
| `event_source` | int | [0, 1] | From event/conference |

**Example:**
```json
{
  "lead_source_quality": 0.75,
  "attribution_touchpoints": 5,
  "paid_channel_source": 1,
  "referral_source": 0,
  "event_source": 0
}
```

### 5. Product Interest Signals (5 features)

Product fit and deployment requirements.

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `product_tier_interest` | int | [1, 3] | Product tier interested in (1=basic, 3=enterprise) |
| `feature_requests_count` | int | [0, ∞) | Feature requests made |
| `use_case_alignment` | float | [0, 1] | Use case fit score |
| `integration_requirements` | int | [0, ∞) | Required integrations |
| `deployment_preference` | int | [0, 2] | 0=cloud, 1=hybrid, 2=on-prem |

**Example:**
```json
{
  "product_tier_interest": 2,
  "feature_requests_count": 2,
  "use_case_alignment": 0.85,
  "integration_requirements": 3,
  "deployment_preference": 0
}
```

## Score Output

### Score Components

The model outputs three related values:

| Component | Range | Description |
|-----------|-------|-------------|
| `raw_score` | [0, 1] | Probability of conversion |
| `bucket` | [1, 5] | Score bucket (5 = highest) |
| `tier` | A-E | Tier label (A = highest) |

### Tier Definitions

| Tier | Bucket | Description | Recommended Action |
|------|--------|-------------|-------------------|
| **A** | 5 | Highest conversion likelihood | Prioritize immediately |
| **B** | 4 | High conversion likelihood | Engage promptly |
| **C** | 3 | Medium conversion likelihood | Nurture and qualify |
| **D** | 2 | Low conversion likelihood | Long-term nurturing |
| **E** | 1 | Lowest conversion likelihood | Minimal investment |

### Score Mapping

```
Raw Score → Bucket → Tier
0.00-0.20 → 1     → E
0.21-0.40 → 2     → D
0.41-0.60 → 3     → C
0.61-0.80 → 4     → B
0.81-1.00 → 5     → A
```

## Feature Engineering Tips

### High-Value Features

Based on typical feature importance:

1. **Behavioral Signals** (40% importance)
   - `decision_maker_contacted`
   - `budget_confirmed`
   - `technical_evaluation_started`
   - `custom_demo_requested`

2. **Engagement Metrics** (30% importance)
   - `pricing_page_visits`
   - `demo_page_visits`
   - `email_click_rate`
   - `website_visits_30d`

3. **Company Firmographics** (20% importance)
   - `company_revenue`
   - `company_employee_count`
   - `industry_tech_score`
   - `company_growth_rate`

4. **Product Interest** (7% importance)
   - `product_tier_interest`
   - `use_case_alignment`

5. **Lead Source** (3% importance)
   - `lead_source_quality`
   - `paid_channel_source`

### Data Collection Best Practices

1. **Real-time Updates**: Update engagement metrics daily
2. **Data Quality**: Validate all inputs before scoring
3. **Missing Values**: Use 0 for optional engagement metrics
4. **Normalization**: Revenue and employee count are normalized internally
5. **Temporal Features**: Keep recency features (days_since_*) updated

### Feature Correlations

Strong correlations exist between:
- Engagement metrics and behavioral signals
- Company size metrics (revenue, employees, subsidiaries)
- Demo-related activities (demo_page_visits, custom_demo_requested)

## Validation Rules

All features undergo validation:

1. **Type checking**: Ensures correct data types
2. **Range validation**: Values must be within specified ranges
3. **Required fields**: All 50 features must be present
4. **Logical consistency**: Related features are checked for consistency

### Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `field required` | Missing feature | Provide all 50 features |
| `value_error.number.not_ge` | Value below minimum | Check range requirements |
| `value_error.number.not_le` | Value above maximum | Check range requirements |
| `type_error.integer` | Float instead of int | Convert to integer |

## API Integration

### Complete Request Example

```json
{
  "lead_id": "LEAD-12345",
  "features": {
    "company_revenue": 5000000.0,
    "company_employee_count": 50,
    "company_age_years": 5.5,
    "company_funding_total": 2000000.0,
    "company_growth_rate": 0.35,
    "industry_tech_score": 0.8,
    "geographic_tier": 1,
    "company_public_status": 0,
    "parent_company_exists": 1,
    "subsidiary_count": 2,
    "website_visits_30d": 45,
    "page_views_30d": 120,
    "avg_session_duration_sec": 180.5,
    "bounce_rate": 0.35,
    "pricing_page_visits": 5,
    "demo_page_visits": 3,
    "documentation_views": 10,
    "email_open_rate": 0.65,
    "email_click_rate": 0.25,
    "emails_received": 8,
    "whitepaper_downloads": 2,
    "webinar_attendance": 1,
    "social_media_engagement": 15,
    "customer_success_interactions": 2,
    "support_ticket_count": 0,
    "days_since_first_touch": 30.0,
    "days_since_last_touch": 2.0,
    "total_touchpoints": 25,
    "multi_channel_engagement": 1,
    "decision_maker_contacted": 1,
    "champion_identified": 1,
    "budget_confirmed": 0,
    "timeline_confirmed": 1,
    "competitor_evaluation": 1,
    "technical_evaluation_started": 1,
    "contract_reviewed": 0,
    "security_questionnaire_completed": 0,
    "roi_calculator_used": 1,
    "custom_demo_requested": 1,
    "integration_questions_asked": 3,
    "lead_source_quality": 0.75,
    "attribution_touchpoints": 5,
    "paid_channel_source": 1,
    "referral_source": 0,
    "event_source": 0,
    "product_tier_interest": 2,
    "feature_requests_count": 2,
    "use_case_alignment": 0.85,
    "integration_requirements": 3,
    "deployment_preference": 0
  }
}
```

### Response Example

```json
{
  "request_id": "f7f46f8d-5b72-4d3d-9a5f-9a5b9800c123",
  "model": {
    "name": "xgboost_lead_score_v100",
    "version": "1.0.0"
  },
  "lead_id": "LEAD-12345",
  "score": {
    "raw_score": 0.82,
    "bucket": 4,
    "tier": "B"
  }
}
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | Initial Release | Initial 50-feature schema |

## Related Documentation

- [API.md](API.md) - API endpoint reference
- [ARCHITECTURE.md](ARCHITECTURE.md) - Model architecture