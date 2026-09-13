"""
app/services/market_similarity_service.py

Explainable, reproducible Market Similarity Engine using scikit-learn NearestNeighbors:
- Leverages the official PostgreSQL Udyam district MSME dataset across 785 Indian districts.
- Feature set: total_msmes, micro_enterprises, small_enterprises, medium_enterprises, micro_share, small_medium_share.
- Standardizes features using scikit-learn StandardScaler.
- Computes multi-dimensional Euclidean proximity using NearestNeighbors(metric="euclidean").
- Returns 3-5 structurally comparable Indian districts with exact Euclidean distances and qualitative observations.
- Absolute Rule: Zero percentage similarity claims (e.g. no "87% similar").
- Resilient failure isolation: Returns graceful fallback structure if database or fit is unavailable.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

from app.schemas.district_msme import DistrictMarketContext
from app.schemas.market_similarity import (
    ComparableDistrictItem,
    ComparableMarketContext,
)
from app.services.market_research_ml_service import (
    market_research_ml_service,
    ML_FEATURES,
)

logger = logging.getLogger(__name__)


class MarketSimilarityService:
    """Service to discover structurally comparable districts using scikit-learn NearestNeighbors."""

    def __init__(self, n_neighbors: int = 5):
        self.n_neighbors = n_neighbors
        self.scaler = StandardScaler()
        self.nn_model = NearestNeighbors(metric="euclidean")
        self._is_fitted = False
        self._dataset_df: Optional[pd.DataFrame] = None
        self._scaled_matrix: Optional[np.ndarray] = None

    def fit(self, db: Session) -> None:
        """Fit the StandardScaler and NearestNeighbors model on all 785 Indian districts."""
        try:
            # Consistent dataset loading from existing ML service loader
            df = market_research_ml_service._load_data(db)
            if df.empty:
                logger.error("No district MSME data found in database for NearestNeighbors fitting.")
                return

            X = df[ML_FEATURES].values
            X_scaled = self.scaler.fit_transform(X)
            self.nn_model.fit(X_scaled)

            self._dataset_df = df
            self._scaled_matrix = X_scaled
            self._is_fitted = True
            logger.info(
                "Successfully fitted MarketSimilarityService NearestNeighbors model on %d districts.",
                len(df),
            )
        except Exception as e:
            logger.error("Failed to fit MarketSimilarityService: %s", e, exc_info=True)
            self._is_fitted = False

    def get_comparable_markets(
        self,
        db: Session,
        district_id: Optional[int] = None,
        district_name: Optional[str] = None,
        state_name: Optional[str] = None,
        lg_dt_code: Optional[str] = None,
        market_context: Optional[DistrictMarketContext] = None,
        top_k: int = 4,
    ) -> ComparableMarketContext:
        """
        Find top_k structurally comparable districts based on standardized MSME features.
        Provides failure isolation: returns graceful fallback structure without raising uncaught exceptions.
        """
        target_dname = district_name or (market_context.district_name if market_context else "Target District")
        target_sname = state_name or (market_context.state_name if market_context else "India")

        if not self._is_fitted:
            self.fit(db)

        if not self._is_fitted or self._dataset_df is None or self._scaled_matrix is None:
            return self._build_fallback(target_dname, target_sname)

        try:
            df = self._dataset_df
            target_idx = None

            # 1. Match target district in dataset
            if district_id:
                m = df[df["district_id"] == district_id]
                if not m.empty:
                    target_idx = m.index[0]

            if target_idx is None and lg_dt_code:
                m = df[df["lg_dt_code"].astype(str) == str(lg_dt_code)]
                if not m.empty:
                    target_idx = m.index[0]

            if target_idx is None and market_context and market_context.lg_dt_code:
                m = df[df["lg_dt_code"].astype(str) == str(market_context.lg_dt_code)]
                if not m.empty:
                    target_idx = m.index[0]

            if target_idx is None and target_dname:
                clean_name = target_dname.strip().upper()
                if state_name:
                    clean_state = state_name.strip().upper()
                    m = df[
                        (df["district_name"].str.upper() == clean_name)
                        & (df["state_name"].str.upper() == clean_state)
                    ]
                    if not m.empty:
                        target_idx = m.index[0]

                if target_idx is None:
                    m = df[df["district_name"].str.upper() == clean_name]
                    if not m.empty:
                        target_idx = m.index[0]

            # 2. Extract or construct target feature vector
            if target_idx is not None:
                target_vector = self._scaled_matrix[target_idx].reshape(1, -1)
                target_dname = df.loc[target_idx, "district_name"]
                target_sname = df.loc[target_idx, "state_name"]
            elif market_context:
                raw_vec = np.array([[
                    int(market_context.total_msmes),
                    int(market_context.micro_enterprises),
                    int(market_context.small_enterprises),
                    int(market_context.medium_enterprises),
                    float(market_context.micro_share),
                    float(market_context.small_medium_share),
                ]])
                target_vector = self.scaler.transform(raw_vec)
            else:
                logger.warning("No matching district found for NearestNeighbors query.")
                return self._build_fallback(target_dname, target_sname)

            # 3. Query NearestNeighbors (fetch top_k + 2 to exclude self and identical duplicates)
            n_to_query = min(top_k + 3, len(df))
            distances, indices = self.nn_model.kneighbors(target_vector, n_neighbors=n_to_query)

            comparable_items: List[ComparableDistrictItem] = []
            rank = 1

            for dist, idx in zip(distances[0], indices[0]):
                # Skip target district itself
                if target_idx is not None and idx == target_idx:
                    continue

                row = df.iloc[idx]
                row_name = str(row["district_name"])
                row_state = str(row["state_name"])

                # Also skip if district name is identical to target
                if row_name.strip().upper() == target_dname.strip().upper():
                    continue

                # Qualitative structural observation
                tot = int(row["total_msmes"])
                mic_pct = float(row["micro_share"])
                sme_pct = float(row["small_medium_share"])

                if sme_pct >= 4.0:
                    observation = (
                        f"Shares an active formal SME supply chain depth ({sme_pct:.1f}% small & medium enterprises) "
                        f"with {tot:,} registered MSMEs in {row_state}."
                    )
                elif tot >= 50000:
                    observation = (
                        f"Demonstrates a comparable high-volume commercial density with {tot:,} MSMEs "
                        f"and {mic_pct:.1f}% micro-enterprise dominance in {row_state}."
                    )
                else:
                    observation = (
                        f"Exhibits a similar localized micro-enterprise ecosystem ({mic_pct:.1f}% Micro) "
                        f"and decentralized retail footprint ({tot:,} MSMEs) in {row_state}."
                    )

                cluster_label = None
                if "cluster_id" in row and hasattr(market_research_ml_service, "_cluster_labels_map"):
                    cid = int(row["cluster_id"])
                    if cid in market_research_ml_service._cluster_labels_map:
                        cluster_label = market_research_ml_service._cluster_labels_map[cid][0]

                comparable_items.append(
                    ComparableDistrictItem(
                        district_id=int(row["district_id"]) if "district_id" in row else None,
                        district_name=row_name,
                        state_name=row_state,
                        similarity_rank=rank,
                        similarity_distance=round(float(dist), 3),
                        total_msmes=tot,
                        micro_share=mic_pct,
                        small_medium_share=sme_pct,
                        cluster_label=cluster_label,
                        qualitative_observation=observation,
                        provenance="MODELLED INDICATOR",
                    )
                )
                rank += 1
                if len(comparable_items) >= top_k:
                    break

            return ComparableMarketContext(
                is_available=True,
                target_district=target_dname,
                target_state=target_sname,
                comparable_districts=comparable_items,
                features_used=ML_FEATURES,
                methodology_notes=[
                    "Features standardized via scikit-learn StandardScaler across all 785 Indian districts.",
                    "Proximity determined using Euclidean distance in standardized 6-feature MSME space.",
                    "NearestNeighbors strictly measures structural enterprise alignment without percentage claims.",
                ],
            )
        except Exception as e:
            logger.error("Error computing comparable markets: %s", e, exc_info=True)
            return self._build_fallback(target_dname, target_sname)

    def _build_fallback(self, target_dname: str, target_sname: str) -> ComparableMarketContext:
        """Failure-isolated graceful fallback."""
        return ComparableMarketContext(
            is_available=False,
            target_district=target_dname,
            target_state=target_sname,
            comparable_districts=[],
            features_used=ML_FEATURES,
            methodology_notes=[
                "NearestNeighbors market similarity service temporarily uninitialized or offline."
            ],
        )


# Singleton Instance
market_similarity_service = MarketSimilarityService()
