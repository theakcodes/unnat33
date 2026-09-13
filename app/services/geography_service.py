"""
app/services/geography_service.py

Service for resolving authoritative geographic centroids and coordinates for districts.
Strictly DB-first: queries PostgreSQL `district_geo_centroids`.
"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.geography import DistrictCoordinates
from app.repositories.district_geo_repository import DistrictGeoRepository


class GeographyService:
    """Service providing authoritative geographic coordinates and elevations for districts."""

    @classmethod
    def get_district_coordinates(
        cls,
        db: Session,
        district_id: Optional[int] = None,
        district_name: Optional[str] = None,
        state_name: Optional[str] = None,
        lg_dt_code: Optional[str] = None,
    ) -> Optional[DistrictCoordinates]:
        """
        Resolve geographic coordinates and elevation for a district.
        Lookup order:
        1. district_id (if provided)
        2. lg_dt_code (if provided)
        3. district_name + optional state_name
        """
        centroid = None

        if district_id:
            centroid = DistrictGeoRepository.get_by_district_id(db, district_id)

        if not centroid and lg_dt_code:
            centroid = DistrictGeoRepository.get_by_district_code(db, lg_dt_code)

        if not centroid and district_name:
            centroid = DistrictGeoRepository.get_by_district_and_state(
                db, district_name=district_name, state_name=state_name
            )

        if not centroid:
            return None

        # Fetch district and state names for complete schema representation
        sql = text("""
            SELECT d.id AS district_id, d.district_name, d.district_code AS lg_dt_code, s.state_name
            FROM districts d
            JOIN states s ON d.state_id = s.id
            WHERE d.id = :d_id
        """)
        row = db.execute(sql, {"d_id": centroid.district_id}).fetchone()
        if not row:
            return None

        m = row._mapping
        return DistrictCoordinates(
            district_id=m["district_id"],
            district_name=m["district_name"],
            state_name=m["state_name"],
            lg_dt_code=m["lg_dt_code"],
            latitude=float(centroid.latitude),
            longitude=float(centroid.longitude),
            elevation_meters=float(centroid.elevation_meters) if centroid.elevation_meters is not None else None,
            source=centroid.source or "open-meteo",
        )
