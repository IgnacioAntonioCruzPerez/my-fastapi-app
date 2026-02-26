"""Building API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.auth import verify_api_key
from app.schemas.building import BuildingResponse
from models import Building, Organization
from app.schemas.organization import OrganizationList

router = APIRouter(prefix="/buildings", tags=["Buildings"])


def _org_to_list(org: Organization) -> OrganizationList:
    return OrganizationList(
        id=org.id,
        name=org.name,
        building_id=org.building_id,
        phone_numbers=[p.phone_number for p in org.phones],
        activity_names=[a.name for a in org.activities],
    )


@router.get("", response_model=List[BuildingResponse])
def list_buildings(
    min_lat: Optional[float] = Query(None),
    max_lat: Optional[float] = Query(None),
    min_lon: Optional[float] = Query(None),
    max_lon: Optional[float] = Query(None),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    List all buildings. Optionally filter by rectangular area (min_lat, max_lat, min_lon, max_lon).
    """
    q = db.query(Building)
    if all(x is not None for x in (min_lat, max_lat, min_lon, max_lon)):
        q = q.filter(
            and_(
                Building.latitude >= min_lat,
                Building.latitude <= max_lat,
                Building.longitude >= min_lon,
                Building.longitude <= max_lon,
            )
        )
    return q.all()


@router.get("/in-area", response_model=List[BuildingResponse])
def list_buildings_in_area(
    lat: float = Query(..., description="Center latitude"),
    lon: float = Query(..., description="Center longitude"),
    radius_km: Optional[float] = Query(None, description="Radius in km"),
    min_lat: Optional[float] = Query(None),
    max_lat: Optional[float] = Query(None),
    min_lon: Optional[float] = Query(None),
    max_lon: Optional[float] = Query(None),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """
    List buildings within radius (km) or rectangular area.
    Either radius_km or (min_lat, max_lat, min_lon, max_lon).
    """
    import math
    if radius_km is not None:
        deg_lat = radius_km / 111.0
        deg_lon = radius_km / (111.0 * max(0.01, abs(math.cos(math.radians(lat)))))
        min_lat, max_lat = lat - deg_lat, lat + deg_lat
        min_lon, max_lon = lon - deg_lon, lon + deg_lon
    elif not all(x is not None for x in (min_lat, max_lat, min_lon, max_lon)):
        from fastapi import HTTPException
        raise HTTPException(400, "Provide radius_km or min_lat, max_lat, min_lon, max_lon")
    buildings = (
        db.query(Building)
        .filter(
            and_(
                Building.latitude >= min_lat,
                Building.latitude <= max_lat,
                Building.longitude >= min_lon,
                Building.longitude <= max_lon,
            )
        )
        .all()
    )
    return buildings


@router.get("/{building_id}", response_model=BuildingResponse)
def get_building(
    building_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """Get building by ID."""
    b = db.query(Building).filter(Building.id == building_id).first()
    if not b:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Building not found")
    return b


@router.get("/{building_id}/organizations", response_model=List[OrganizationList])
def list_organizations_in_building(
    building_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db),
):
    """List all organizations in a specific building."""
    orgs = db.query(Organization).filter(Organization.building_id == building_id).all()
    return [_org_to_list(o) for o in orgs]
