"""Activity API endpoints (tree, max 3 levels)."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import verify_api_key
from app.schemas.activity import ActivityResponse, ActivityTree
from models import Activity

router = APIRouter(prefix="/activities", tags=["Activities"])


def _build_tree(activity: Activity, all_activities: list) -> ActivityTree:
    children = [a for a in all_activities if a.parent_id == activity.id]
    return ActivityTree(
        id=activity.id,
        name=activity.name,
        parent_id=activity.parent_id,
        level=activity.level,
        children=[_build_tree(c, all_activities) for c in children],
    )


@router.get("", response_model=List[ActivityResponse])
def list_activities(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """List all activities (flat)."""
    return db.query(Activity).all()


@router.get("/tree", response_model=List[ActivityTree])
def list_activities_tree(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """List activities as a tree (max 3 levels)."""
    all_activities = db.query(Activity).all()
    roots = [a for a in all_activities if a.parent_id is None]
    return [_build_tree(r, all_activities) for r in roots]


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get activity by ID."""
    a = db.query(Activity).filter(Activity.id == activity_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")
    return a
