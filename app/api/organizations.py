"""Organization API endpoints."""
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.auth import verify_api_key
from app.schemas.organization import OrganizationResponse, OrganizationList
from models import Organization, Building, Activity, OrganizationPhone

router = APIRouter(prefix="/organizations", tags=["Organizations"])


def _org_to_list(org: Organization) -> OrganizationList:
    return OrganizationList(
        id=org.id,
        name=org.name,
        building_name=org.building.address if org.building else "",
        phone_numbers=[p.phone_number for p in org.phones],
        activity_names=[a.name for a in org.activities],
    )


def _org_to_response(org: Organization) -> OrganizationResponse:
    from app.schemas.building import BuildingResponse
    from app.schemas.activity import ActivityResponse
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        building_id=org.building_id,
        building=BuildingResponse.model_validate(org.building) if org.building else None,
        activities=[ActivityResponse.model_validate(a) for a in org.activities],
        phone_numbers=[p.phone_number for p in org.phones],
    )


@router.get("", response_model=List[OrganizationList])
def list_organizations(
    building_id: Optional[int] = Query(None, description="Filter by building ID"),
    activity_id: Optional[int] = Query(None, description="Filter by activity ID (exact)"),
    name: Optional[str] = Query(None, description="Search by organization name (substring)"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    List organizations with optional filters: building_id, activity_id, or name search.
    """
    q = db.query(Organization)
    if building_id is not None:
        q = q.filter(Organization.building_id == building_id)
    if activity_id is not None:
        q = q.join(Organization.activities).filter(Activity.id == activity_id)
    if name:
        q = q.filter(Organization.name.ilike(f"%{name}%"))
    q = q.distinct()
    orgs = q.all()
    return [_org_to_list(o) for o in orgs]


@router.get("/by-building/{building_id}", response_model=List[OrganizationList])
def list_organizations_by_building(
    building_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """List all organizations located in a specific building."""
    orgs = db.query(Organization).filter(Organization.building_id == building_id).all()
    return [_org_to_list(o) for o in orgs]


@router.get("/by-activity/{activity_id}", response_model=List[OrganizationList])
def list_organizations_by_activity(
    activity_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """List all organizations that belong to a specified activity (exact activity ID)."""
    orgs = (
        db.query(Organization)
        .join(Organization.activities)
        .filter(Activity.id == activity_id)
        .distinct()
        .all()
    )
    return [_org_to_list(o) for o in orgs]


@router.get("/by-activity-tree/{activity_id}", response_model=List[OrganizationList])
def list_organizations_by_activity_tree(
    activity_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    Search by activity type including descendants. E.g. activity "Food" returns
    organizations with Food, Meat, Dairy, etc.
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    # Collect activity_id and all descendant ids (children, grandchildren)
    def collect_ids(a: Activity) -> set:
        ids = {a.id}
        for c in a.children:
            ids |= collect_ids(c)
        return ids
    ids = collect_ids(activity)
    orgs = (
        db.query(Organization)
        .join(Organization.activities)
        .filter(Activity.id.in_(ids))
        .distinct()
        .all()
    )
    return [_org_to_list(o) for o in orgs]


@router.get("/search-by-name", response_model=List[OrganizationList])
def search_organizations_by_name(
    q: str = Query(..., min_length=1, description="Organization name search"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Search for organizations by name (case-insensitive substring)."""
    orgs = db.query(Organization).filter(Organization.name.ilike(f"%{q}%")).all()
    return [_org_to_list(o) for o in orgs]


@router.get("/in-area", response_model=List[OrganizationList])
def list_organizations_in_area(
    lat: float = Query(..., description="Center latitude"),
    lon: float = Query(..., description="Center longitude"),
    radius_km: Optional[float] = Query(None, description="Radius in km (circular area)"),
    min_lat: Optional[float] = Query(None, description="Min latitude (rectangular area)"),
    max_lat: Optional[float] = Query(None, description="Max latitude"),
    min_lon: Optional[float] = Query(None, description="Min longitude"),
    max_lon: Optional[float] = Query(None, description="Max longitude"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    List organizations within radius (km) or within a rectangular bounding box.
    Either provide radius_km or (min_lat, max_lat, min_lon, max_lon).
    """
    # Approximate: 1 degree lat ~ 111 km, 1 degree lon ~ 111*cos(lat) km
    if radius_km is not None:
        deg_lat = radius_km / 111.0
        deg_lon = radius_km / (111.0 * max(0.01, abs(math.cos(math.radians(lat)))))
        min_lat, max_lat = lat - deg_lat, lat + deg_lat
        min_lon, max_lon = lon - deg_lon, lon + deg_lon
    elif min_lat is None or max_lat is None or min_lon is None or max_lon is None:
        raise HTTPException(
            status_code=400,
            detail="Provide either radius_km or min_lat, max_lat, min_lon, max_lon",
        )
    sub = (
        db.query(Building.id)
        .filter(
            and_(
                Building.latitude >= min_lat,
                Building.latitude <= max_lat,
                Building.longitude >= min_lon,
                Building.longitude <= max_lon,
            )
        )
        .subquery()
    )
    orgs = db.query(Organization).filter(Organization.building_id.in_(sub)).all()
    return [_org_to_list(o) for o in orgs]


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Display organization information by its ID."""
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return _org_to_response(org)
