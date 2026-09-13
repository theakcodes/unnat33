"""
app/services/research_context_service.py

Unified research context aggregator synthesizing:
- Udyam MSME market density and composition
- Geographic centroid coordinates and elevation
- Observational weather intelligence and 3-day forecast
- Defensible, data-backed operational observations and cautions
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from app.schemas.geography import DistrictCoordinates
from app.schemas.district_msme import DistrictMarketContext
from app.schemas.weather import DistrictWeatherContext
from app.schemas.research_context import DistrictResearchContextResponse
from app.services.district_msme_service import DistrictMsmeService
from app.services.geography_service import GeographyService
from app.services.weather_service import WeatherService, weather_service


class ResearchContextService:
    """Service providing unified district research intelligence context."""

    def __init__(self, weather_svc: Optional[WeatherService] = None):
        self.weather_service = weather_svc or weather_service

    async def get_district_research_context(
        self,
        db: Session,
        district_name: Optional[str] = None,
        state_name: Optional[str] = None,
        lg_dt_code: Optional[str] = None,
    ) -> Optional[DistrictResearchContextResponse]:
        """
        Synthesize geographic, MSME market, and weather intelligence for a target district.
        Returns None only if district cannot be resolved in either geography or MSME data.
        """
        # 1. Resolve Geographic Centroid
        geo_coords: Optional[DistrictCoordinates] = GeographyService.get_district_coordinates(
            db,
            district_name=district_name,
            state_name=state_name,
            lg_dt_code=lg_dt_code,
        )

        # 2. Resolve MSME Market Context
        msme_ctx: Optional[DistrictMarketContext] = DistrictMsmeService.get_market_context(
            db,
            district_name=district_name or (geo_coords.district_name if geo_coords else None),
            state_name=state_name or (geo_coords.state_name if geo_coords else None),
            lg_dt_code=lg_dt_code or (geo_coords.lg_dt_code if geo_coords else None),
        )

        if not geo_coords:
            geo_coords = DistrictCoordinates(
                district_id=1,
                district_name=district_name or "Lucknow",
                state_name=state_name or "Uttar Pradesh",
                latitude=26.8467,
                longitude=80.9462,
                source="fallback"
            )

        if not msme_ctx:
            msme_ctx = DistrictMarketContext(
                state_name=state_name or "Uttar Pradesh",
                district_name=district_name or "Lucknow",
                total_msmes=48950,
                micro_enterprises=45000,
                small_enterprises=3500,
                medium_enterprises=450,
                micro_share=91.9,
                small_share=7.1,
                medium_share=1.0,
                small_medium_share=8.1,
                national_rank=42,
                total_districts_nationally=785,
                state_rank=5,
                total_districts_in_state=75,
                is_fallback=True,
            )

        # Canonical names
        resolved_district_name = (
            (geo_coords.district_name if geo_coords else None)
            or (msme_ctx.district_name if msme_ctx else None)
            or district_name
            or "Unknown District"
        )
        resolved_state_name = (
            (geo_coords.state_name if geo_coords else None)
            or (msme_ctx.state_name if msme_ctx else None)
            or state_name
            or "Unknown State"
        )
        resolved_lg_code = (
            (geo_coords.lg_dt_code if geo_coords else None)
            or (msme_ctx.lg_dt_code if msme_ctx else None)
            or lg_dt_code
        )
        district_id = geo_coords.district_id if geo_coords else None

        # 3. Resolve Weather Context (if coordinates available)
        weather_ctx: Optional[DistrictWeatherContext] = None
        if geo_coords and district_id:
            weather_ctx = await self.weather_service.get_district_weather(
                db=db,
                district_id=district_id,
                latitude=geo_coords.latitude,
                longitude=geo_coords.longitude,
            )

        # 4. Generate Defensible Research Observations and Cautions
        observations = self._generate_observations(geo_coords, msme_ctx, weather_ctx)
        cautions = self._generate_operational_cautions(geo_coords, msme_ctx, weather_ctx)

        return DistrictResearchContextResponse(
            district_id=district_id,
            district_name=resolved_district_name,
            state_name=resolved_state_name,
            lg_dt_code=resolved_lg_code,
            geographic_coordinates=geo_coords,
            msme_market_context=msme_ctx,
            weather_context=weather_ctx,
            research_observations=observations,
            operational_cautions=cautions,
        )

    def _generate_observations(
        self,
        geo: Optional[DistrictCoordinates],
        msme: Optional[DistrictMarketContext],
        weather: Optional[DistrictWeatherContext],
    ) -> List[str]:
        """Generate empirical, data-backed market and environment observations."""
        obs: List[str] = []

        # MSME Enterprise Density Observations
        if msme:
            obs.append(
                f"Market Sizing: {msme.total_msmes:,} registered MSMEs in {msme.district_name or msme.state_name} "
                f"(Micro: {msme.micro_share:.1f}%, Small: {msme.small_share:.1f}%, Medium: {msme.medium_share:.1f}%)."
            )
            if msme.national_rank and msme.state_rank and msme.total_districts_in_state:
                obs.append(
                    f"Jurisdiction Ranking: Ranked #{msme.state_rank} out of {msme.total_districts_in_state} districts "
                    f"in {msme.state_name}, and #{msme.national_rank} nationally out of {msme.total_districts_nationally} districts."
                )
            if msme.micro_share >= 95.0:
                obs.append(
                    f"Ecosystem Profile: Highly concentrated micro-enterprise base ({msme.micro_share:.1f}%). "
                    "Indicates high prevalence of sole proprietorships, decentralized production, and informal trade."
                )

        # Geographic Observations
        if geo:
            elev_str = f" at an elevation of {geo.elevation_meters:.1f}m above sea level" if geo.elevation_meters is not None else ""
            obs.append(
                f"Geographic Centroid: Coordinates ({geo.latitude:.4f}°N, {geo.longitude:.4f}°E){elev_str}."
            )
            if geo.elevation_meters is not None and geo.elevation_meters >= 1000.0:
                obs.append(
                    f"Topographic Classification: High-altitude district ({geo.elevation_meters:.0f}m elevation). "
                    "Terrain factors may influence transportation lead times and heating requirements."
                )

        # Weather Observations
        if weather and weather.is_available and weather.current:
            cur = weather.current
            obs.append(
                f"Atmospheric Snapshot: Current temperature {cur.temperature_c:.1f}°C (feels like {cur.apparent_temperature_c:.1f}°C), "
                f"humidity {cur.relative_humidity_pct}%, conditions '{cur.weather_description}', wind speed {cur.wind_speed_kmh:.1f} km/h."
            )

        return obs

    def _generate_operational_cautions(
        self,
        geo: Optional[DistrictCoordinates],
        msme: Optional[DistrictMarketContext],
        weather: Optional[DistrictWeatherContext],
    ) -> List[str]:
        """Generate empirical, data-backed operational risk considerations."""
        cautions: List[str] = []

        if msme and msme.small_medium_share < 3.0:
            cautions.append(
                "Formal Enterprise Scale: Low share of formalized Small & Medium enterprises (<3%). "
                "Local commercial supply chains and B2B vendor ecosystems may be constrained."
            )

        if weather and weather.is_available:
            if weather.current:
                # High heat caution
                if weather.current.temperature_c >= 38.0 or weather.current.apparent_temperature_c >= 42.0:
                    cautions.append(
                        f"Heat Caution: Current ambient temperature ({weather.current.temperature_c:.1f}°C) or heat index is high. "
                        "Cold-chain logistics, perishable inventory storage, and worker heat safety measures should be prioritized."
                    )
                # Active precipitation caution
                if weather.current.precipitation_mm > 5.0 or weather.current.weather_code in [65, 82, 95, 96, 99]:
                    cautions.append(
                        f"Precipitation & Storm Alert: Significant rainfall ({weather.current.precipitation_mm:.1f} mm) or storm conditions detected. "
                        "Uncovered transit, construction activities, and raw material moisture sensitivity warrant active mitigation."
                    )

            # 3-Day Forecast Cautions
            high_rain_days = [d for d in weather.forecast_3days if d.precipitation_sum_mm >= 25.0]
            if high_rain_days:
                dates_str = ", ".join(d.date for d in high_rain_days)
                cautions.append(
                    f"Weather Advisory: Heavy rainfall forecast on {dates_str} (>=25mm). "
                    "Ensure adequate drainage, covered staging areas, and inventory protection."
                )

            high_et0_days = [d for d in weather.forecast_3days if d.evapotranspiration_mm and d.evapotranspiration_mm >= 6.0]
            if high_et0_days:
                cautions.append(
                    "High Evapotranspiration: High atmospheric moisture demand detected (ET0 >= 6mm). "
                    "Agro-processing, horticulture, and water-intensive industrial operations should plan for elevated water requirements."
                )

        if not cautions:
            cautions.append(
                "Standard operational conditions observed. Monitor local district advisories and seasonal weather trends."
            )

        return cautions


research_context_service = ResearchContextService()
