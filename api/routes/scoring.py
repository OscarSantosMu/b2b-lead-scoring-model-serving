"""
Lead scoring API routes.
"""

import logging
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from api.app.datalake import write_scoring_result
from api.app.model import get_model
from api.middleware.auth import get_current_user
from api.schemas.lead_features import (
    TIER_DEFINITIONS,
    ModelInfo,
    RankingInfo,
    ScoreInfo,
    ScoringRequest,
    ScoringResponse,
    TimingInfo,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["scoring"])

API_VERSION = "1.0.0"


def build_scoring_response(
    request_id: str,
    lead_id: str,
    raw_score: float,
    bucket: int,
    tier: str,
    latency_ms: float,
    model_name: str,
    model_version: str,
    include_details: bool = False,
) -> ScoringResponse:
    """Build the scoring response with optional details."""
    # Build score info
    score_info = ScoreInfo(
        raw_score=raw_score,
        bucket=bucket,
        tier=tier,
        ranking=(RankingInfo(tier_definition=TIER_DEFINITIONS.copy()) if include_details else None),
    )

    # Build response
    response = ScoringResponse(
        request_id=request_id,
        model=ModelInfo(name=model_name, version=model_version),
        lead_id=lead_id,
        score=score_info,
        timing=TimingInfo(latency_ms=round(latency_ms, 2)) if include_details else None,
        api_version=API_VERSION if include_details else None,
    )

    return response


@router.post(
    "/score",
    response_model=ScoringResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Score a single lead",
    description="Score a B2B lead based on 50 features. Returns score bucket (1-5), tier (A-E), and raw probability.",
)
async def score_lead(
    request: ScoringRequest,
    background_tasks: BackgroundTasks,
    include_details: bool = Query(
        default=False,
        description="Include additional details like timing, tier definitions, and API version",
    ),
    current_user: dict = Depends(get_current_user),
) -> ScoringResponse:
    """Score a single lead."""
    request_id = str(uuid.uuid4())
    try:
        model = get_model()

        # Convert features to dict
        features_dict = request.features.model_dump()

        # Make prediction
        raw_score, bucket, tier, latency_ms = model.predict(features_dict)

        # Build response
        response = build_scoring_response(
            request_id=request_id,
            lead_id=request.lead_id,
            raw_score=raw_score,
            bucket=bucket,
            tier=tier,
            latency_ms=latency_ms,
            model_name=f"xgboost_lead_score_v{model.model_version.replace('.', '')}",
            model_version=model.model_version,
            include_details=include_details,
        )

        # Write result to data lake in background (non-blocking)
        timestamp = datetime.now(UTC).isoformat()
        background_tasks.add_task(
            write_scoring_result,
            lead_id=request.lead_id,
            bucket=bucket,
            tier=tier,
            raw_score=raw_score,
            model_version=model.model_version,
            timestamp=timestamp,
            features=features_dict,
        )

        logger.info(
            "Lead scored successfully",
            extra={
                "request_id": request_id,
                "lead_id": request.lead_id,
                "raw_score": raw_score,
                "bucket": bucket,
                "tier": tier,
            },
        )

        return response

    except Exception as e:
        logger.error(
            f"Error scoring lead: {e}",
            extra={"lead_id": request.lead_id, "request_id": request_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scoring lead: {str(e)}",
        ) from e


@router.post(
    "/score/batch",
    response_model=list[ScoringResponse],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    summary="Score multiple leads",
    description="Score multiple B2B leads in a single request",
)
async def score_leads_batch(
    requests: list[ScoringRequest],
    background_tasks: BackgroundTasks,
    include_details: bool = Query(
        default=False,
        description="Include additional details like timing, tier definitions, and API version",
    ),
    current_user: dict = Depends(get_current_user),
) -> list[ScoringResponse]:
    """Score multiple leads in batch."""
    if len(requests) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 leads per batch request",
        )

    try:
        model = get_model()
        responses = []
        # Use consistent timestamp for all leads in the batch
        batch_timestamp = datetime.now(UTC).isoformat()

        for req in requests:
            request_id = str(uuid.uuid4())
            features_dict = req.features.model_dump()
            raw_score, bucket, tier, latency_ms = model.predict(features_dict)

            response = build_scoring_response(
                request_id=request_id,
                lead_id=req.lead_id,
                raw_score=raw_score,
                bucket=bucket,
                tier=tier,
                latency_ms=latency_ms,
                model_name=f"xgboost_lead_score_v{model.model_version.replace('.', '')}",
                model_version=model.model_version,
                include_details=include_details,
            )
            responses.append(response)

            # Write each result to data lake in background
            background_tasks.add_task(
                write_scoring_result,
                lead_id=req.lead_id,
                bucket=bucket,
                tier=tier,
                raw_score=raw_score,
                model_version=model.model_version,
                timestamp=batch_timestamp,
                features=features_dict,
            )

        logger.info(f"Batch scored {len(requests)} leads successfully")

        return responses

    except Exception as e:
        logger.error(f"Error in batch scoring: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch scoring: {str(e)}",
        ) from e


@router.get(
    "/model/info",
    summary="Get model information",
    description="Retrieve model version, features, and metadata",
)
async def get_model_info(
    current_user: dict = Depends(get_current_user),
):
    """Get model information."""
    try:
        model = get_model()
        return model.get_model_info()
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting model info: {str(e)}",
        ) from e


@router.get(
    "/model/features",
    summary="Get feature names",
    description="Retrieve the list of 50 features used by the model",
)
async def get_feature_names(
    current_user: dict = Depends(get_current_user),
):
    """Get feature names."""
    try:
        model = get_model()
        return {
            "features": model.feature_names,
            "count": len(model.feature_names),
        }
    except Exception as e:
        logger.error(f"Error getting features: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting features: {str(e)}",
        ) from e


@router.get(
    "/model/importance",
    summary="Get feature importance",
    description="Retrieve feature importance scores from the model",
)
async def get_feature_importance(
    current_user: dict = Depends(get_current_user),
):
    """Get feature importance."""
    try:
        model = get_model()
        importance = model.get_feature_importance()

        # Sort by importance
        sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)

        return {
            "importance": dict(sorted_importance),
            "top_10": sorted_importance[:10],
        }
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting feature importance: {str(e)}",
        ) from e
