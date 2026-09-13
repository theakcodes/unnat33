from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.schemas.district_msme import DistrictMarketContext
from app.repositories.district_msme_repository import district_msme_repository


class DistrictMsmeService:
    """Service providing empirical district MSME market-context indicators.
    
    IMPORTANT:
    These metrics are empirical market-context indicators derived from Udyam records.
    They do NOT constitute proof of individual business success or financial viability.
    """

    @classmethod
    def get_market_context(
        cls,
        db: Session,
        district_name: Optional[str] = None,
        state_name: Optional[str] = None,
        lg_dt_code: Optional[str] = None,
    ) -> Optional[DistrictMarketContext]:
        """Resolve market context with priority: LGD Code -> District + State -> State-level fallback."""
        record: Optional[Dict[str, Any]] = None
        is_fallback = False

        # 1. Primary Lookup: LGD Code if supplied
        if lg_dt_code:
            record = district_msme_repository.get_by_lgd_code(db, lg_dt_code=lg_dt_code)

        # 2. Secondary Lookup: District Name + State Name
        if not record and district_name:
            record = district_msme_repository.get_by_district_and_state(
                db, district_name=district_name, state_name=state_name
            )

        # 3. Tertiary Fallback: State-level aggregate if district not found or not supplied
        if not record and state_name:
            st_record = district_msme_repository.get_state_aggregate(db, state_name_or_code=state_name)
            if st_record:
                is_fallback = True
                tot = int(st_record["total_msmes"])
                mic = int(st_record["micro_enterprises"])
                sm = int(st_record["small_enterprises"])
                med = int(st_record["medium_enterprises"])
                
                return DistrictMarketContext(
                    geographic_level="STATE",
                    state_name=st_record["state_name"],
                    state_code=st_record.get("state_code"),
                    district_name=None,
                    lg_dt_code=None,
                    total_msmes=tot,
                    micro_enterprises=mic,
                    small_enterprises=sm,
                    medium_enterprises=med,
                    micro_share=round((mic / tot * 100), 2) if tot > 0 else 0.0,
                    small_share=round((sm / tot * 100), 2) if tot > 0 else 0.0,
                    medium_share=round((med / tot * 100), 2) if tot > 0 else 0.0,
                    small_medium_share=round(((sm + med) / tot * 100), 2) if tot > 0 else 0.0,
                    national_rank=None,
                    total_districts_nationally=785,
                    state_rank=None,
                    total_districts_in_state=int(st_record.get("total_districts_in_state") or 0),
                    is_fallback=True,
                    market_context_notes=[
                        "District name was unprovided or unresolvable; using State-level aggregate metrics as fallback context.",
                        "Empirical indicator derived from Udyam registration records; does not represent business success probability."
                    ]
                )

        if not record:
            return None

        # Build District-level context model
        tot = int(record["total_msmes"])
        mic = int(record["micro_enterprises"])
        sm = int(record["small_enterprises"])
        med = int(record["medium_enterprises"])

        return DistrictMarketContext(
            geographic_level="DISTRICT",
            state_name=record["state_name"],
            state_code=record.get("state_code"),
            district_name=record["district_name"],
            lg_dt_code=str(record["lg_dt_code"]),
            total_msmes=tot,
            micro_enterprises=mic,
            small_enterprises=sm,
            medium_enterprises=med,
            micro_share=round((mic / tot * 100), 2) if tot > 0 else 0.0,
            small_share=round((sm / tot * 100), 2) if tot > 0 else 0.0,
            medium_share=round((med / tot * 100), 2) if tot > 0 else 0.0,
            small_medium_share=round(((sm + med) / tot * 100), 2) if tot > 0 else 0.0,
            national_rank=int(record["national_rank"]),
            total_districts_nationally=785,
            state_rank=int(record["state_rank"]),
            total_districts_in_state=int(record["total_districts_in_state"]),
            is_fallback=False,
            market_context_notes=[
                f"District market indicator: {record['district_name']} ranks #{record['national_rank']} nationally and #{record['state_rank']} within {record['state_name']}.",
                "Market-context indicator only; does not represent individual business viability or guarantee scheme approval."
            ]
        )


district_msme_service = DistrictMsmeService()
