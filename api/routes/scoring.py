"""
Lead scoring API routes.
"""

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from api.app.model import get_model
from api.middleware.auth import get_current_user
from api.schemas.lead_features import ScoringRequest, ScoringResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["scoring"])


@router.post(
    "/score",
    response_model=ScoringResponse,
    status_code=status.HTTP_200_OK,
    summary="Score a single lead",
    description="Score a B2B lead based on 50 features and return probability, tier, and confidence",
)
async def score_lead(
    request: ScoringRequest,
    current_user: dict = Depends(get_current_user),
) -> ScoringResponse:
    """Score a single lead."""
    try:
        model = get_model()

        # Convert features to dict
        features_dict = request.features.model_dump()

        # Make prediction
        score, confidence, tier = model.predict(features_dict)

        # Create response
        response = ScoringResponse(
            lead_id=request.lead_id,
            score=score,
            tier=tier,
            confidence=confidence,
            model_version=model.model_version,
            timestamp=datetime.now(UTC).isoformat(),
        )

        logger.info(
            "Lead scored successfully",
            extra={
                "lead_id": request.lead_id,
                "score": score,
                "tier": tier,
                "confidence": confidence,
            },
        )

        return response

    except Exception as e:
        logger.error(f"Error scoring lead: {e}", extra={"lead_id": request.lead_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scoring lead: {str(e)}",
        ) from e


@router.post(
    "/score/batch",
    response_model=list[ScoringResponse],
    status_code=status.HTTP_200_OK,
    summary="Score multiple leads",
    description="Score multiple B2B leads in a single request",
)
async def score_leads_batch(
    requests: list[ScoringRequest],
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

        for req in requests:
            features_dict = req.features.model_dump()
            score, confidence, tier = model.predict(features_dict)

            response = ScoringResponse(
                lead_id=req.lead_id,
                score=score,
                tier=tier,
                confidence=confidence,
                model_version=model.model_version,
                timestamp=datetime.now(UTC).isoformat(),
            )
            responses.append(response)

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
