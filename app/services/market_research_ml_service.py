"""
app/services/market_research_ml_service.py

Basic, explainable, and reproducible Machine Learning Market Research Service:
- Leverages official PostgreSQL Udyam district MSME records across all 785 Indian districts.
- Features: total_msmes, micro_enterprises, small_enterprises, medium_enterprises, micro_share, small_medium_share.
- Missing-value handling: zero imputation for unpopulated categories.
- Preprocessing: scikit-learn StandardScaler.
- Primary Model: scikit-learn KMeans clustering (K=4, random_state=42, n_init=10).
- Reproducible, deterministic results with empirical cluster archetype labelling.
- Documented, transparent Market Research Indicator calculation.
- Resilient failure isolation: graceful fallback without raising uncaught exceptions.
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from app.schemas.district_msme import DistrictMarketContext
from app.schemas.market_intelligence import (
    MarketResearchMLAnalysis,
    ClusterQuantitativeIndicators,
)

logger = logging.getLogger(__name__)

# Configurable Weights for Transparent Market Research Indicator
WEIGHT_NATIONAL_DENSITY = 0.40
WEIGHT_STATE_DENSITY = 0.30
WEIGHT_SME_DEPTH = 0.30

# Feature Set Definition
ML_FEATURES = [
    "total_msmes",
    "micro_enterprises",
    "small_enterprises",
    "medium_enterprises",
    "micro_share",
    "small_medium_share",
]


class MarketResearchMLService:
    """Reusable scikit-learn KMeans clustering and market indicator service."""

    def __init__(self, n_clusters: int = 4, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = KMeans(n_clusters=self.n_clusters, random_state=self.random_state, n_init=10)
        self._is_fitted = False
        self._dataset_df: Optional[pd.DataFrame] = None
        self._cluster_labels_map: Dict[int, Tuple[str, str]] = {}
        self._cluster_distribution: Dict[str, int] = {}
        self._cluster_means: Dict[int, Dict[str, float]] = {}

    def _load_data(self, db: Session) -> pd.DataFrame:
        """Load cross-sectional MSME district records for all 785 districts from PostgreSQL."""
        sql = """
            SELECT 
                d.id AS district_id,
                d.district_code AS lg_dt_code,
                d.district_name,
                s.id AS state_id,
                s.state_name,
                s.state_code,
                COALESCE(m.micro_enterprises, 0) AS micro_enterprises,
                COALESCE(m.small_enterprises, 0) AS small_enterprises,
                COALESCE(m.medium_enterprises, 0) AS medium_enterprises,
                (COALESCE(m.micro_enterprises, 0) + COALESCE(m.small_enterprises, 0) + COALESCE(m.medium_enterprises, 0)) AS total_msmes,
                ROUND((COALESCE(m.micro_enterprises, 0)::numeric / NULLIF(COALESCE(m.micro_enterprises, 0) + COALESCE(m.small_enterprises, 0) + COALESCE(m.medium_enterprises, 0), 0) * 100), 2) AS micro_share,
                ROUND((COALESCE(m.small_enterprises, 0)::numeric / NULLIF(COALESCE(m.micro_enterprises, 0) + COALESCE(m.small_enterprises, 0) + COALESCE(m.medium_enterprises, 0), 0) * 100), 2) AS small_share,
                ROUND((COALESCE(m.medium_enterprises, 0)::numeric / NULLIF(COALESCE(m.micro_enterprises, 0) + COALESCE(m.small_enterprises, 0) + COALESCE(m.medium_enterprises, 0), 0) * 100), 2) AS medium_share,
                ROUND(((COALESCE(m.small_enterprises, 0) + COALESCE(m.medium_enterprises, 0))::numeric / NULLIF(COALESCE(m.micro_enterprises, 0) + COALESCE(m.small_enterprises, 0) + COALESCE(m.medium_enterprises, 0), 0) * 100), 2) AS small_medium_share,
                RANK() OVER (ORDER BY (COALESCE(m.micro_enterprises, 0) + COALESCE(m.small_enterprises, 0) + COALESCE(m.medium_enterprises, 0)) DESC) AS national_rank,
                RANK() OVER (PARTITION BY s.id ORDER BY (COALESCE(m.micro_enterprises, 0) + COALESCE(m.small_enterprises, 0) + COALESCE(m.medium_enterprises, 0)) DESC) AS state_rank,
                COUNT(*) OVER (PARTITION BY s.id) AS total_districts_in_state
            FROM districts d
            JOIN states s ON d.state_id = s.id
            LEFT JOIN msme_district_data m ON m.district_id = d.id
            ORDER BY d.id ASC;
        """
        df = pd.read_sql(text(sql), db.bind)
        # Robust missing-value handling
        df["total_msmes"] = df["total_msmes"].fillna(0).astype(int)
        df["micro_enterprises"] = df["micro_enterprises"].fillna(0).astype(int)
        df["small_enterprises"] = df["small_enterprises"].fillna(0).astype(int)
        df["medium_enterprises"] = df["medium_enterprises"].fillna(0).astype(int)
        df["micro_share"] = df["micro_share"].fillna(100.0).astype(float)
        df["small_share"] = df["small_share"].fillna(0.0).astype(float)
        df["medium_share"] = df["medium_share"].fillna(0.0).astype(float)
        df["small_medium_share"] = df["small_medium_share"].fillna(0.0).astype(float)
        df["national_rank"] = df["national_rank"].fillna(785).astype(int)
        df["state_rank"] = df["state_rank"].fillna(1).astype(int)
        df["total_districts_in_state"] = df["total_districts_in_state"].fillna(1).astype(int)
        return df

    def fit(self, db: Session) -> None:
        """Fit the StandardScaler and KMeans clustering pipeline on all Indian districts."""
        try:
            df = self._load_data(db)
            if df.empty:
                logger.error("No district MSME data found in database to fit KMeans.")
                return

            X = df[ML_FEATURES].values
            X_scaled = self.scaler.fit_transform(X)
            cluster_assignments = self.model.fit_predict(X_scaled)
            df["cluster_id"] = cluster_assignments

            # Compute empirical cluster profiles and dynamic labels
            self._cluster_distribution = {
                str(cid): int((df["cluster_id"] == cid).sum())
                for cid in sorted(df["cluster_id"].unique())
            }

            self._cluster_means = {}
            self._cluster_labels_map = {}

            for cid in sorted(df["cluster_id"].unique()):
                sub = df[df["cluster_id"] == cid]
                mean_tot = float(sub["total_msmes"].mean())
                mean_mic = float(sub["micro_share"].mean())
                mean_sme = float(sub["small_medium_share"].mean())

                self._cluster_means[cid] = {
                    "mean_total_msmes": mean_tot,
                    "mean_micro_share": mean_mic,
                    "mean_sme_share": mean_sme,
                }

                # Empirical label assignment based on cluster characteristics
                if mean_tot >= 200000.0:
                    label = "Metropolitan Commercial & Industrial Hub"
                    desc = (
                        f"High-density metropolitan economic center with extensive enterprise volume "
                        f"(mean {mean_tot:,.0f} MSMEs) and established multi-tier commercial markets."
                    )
                elif mean_sme >= 4.5:
                    label = "Formalized SME-Concentrated Industrial Market"
                    desc = (
                        f"Specialized regional industrial or commercial hub with elevated formal SME density "
                        f"(mean {mean_sme:.1f}% Small & Medium enterprises vs national 1.3% baseline)."
                    )
                elif mean_tot >= 35000.0:
                    label = "Medium-to-High Density Micro-Dominant Market"
                    desc = (
                        f"Substantial commercial center dominated by micro-enterprises "
                        f"(mean {mean_mic:.1f}% Micro) with moderate formal vendor integration."
                    )
                else:
                    label = "Emerging / Lower-Density Micro-Enterprise Market"
                    desc = (
                        f"Decentralized rural or developing district with lower aggregate enterprise density "
                        f"(mean {mean_tot:,.0f} MSMEs) and reliance on micro-enterprises ({mean_mic:.1f}% Micro)."
                    )

                self._cluster_labels_map[cid] = (label, desc)

            self._dataset_df = df
            self._is_fitted = True
            logger.info(
                "Successfully trained MarketResearchMLService KMeans model on %d districts with %d clusters.",
                len(df),
                self.n_clusters,
            )
        except Exception as e:
            logger.error("Failed to fit MarketResearchMLService: %s", e, exc_info=True)
            self._is_fitted = False

    def get_analysis_for_district(
        self,
        db: Session,
        district_id: Optional[int] = None,
        market_context: Optional[DistrictMarketContext] = None,
    ) -> MarketResearchMLAnalysis:
        """
        Generate structured ML market analysis for a target district.
        Provides failure isolation: returns graceful fallback structure if ML model cannot fit.
        """
        if not self._is_fitted:
            self.fit(db)

        if not self._is_fitted or self._dataset_df is None:
            # Failure isolation: graceful fallback
            return self._build_fallback_analysis(market_context)

        try:
            # 1. Match district row in trained dataset
            district_row = None
            if district_id:
                matched = self._dataset_df[self._dataset_df["district_id"] == district_id]
                if not matched.empty:
                    district_row = matched.iloc[0]

            if district_row is None and market_context:
                if market_context.lg_dt_code:
                    matched = self._dataset_df[
                        self._dataset_df["lg_dt_code"].astype(str) == str(market_context.lg_dt_code)
                    ]
                    if not matched.empty:
                        district_row = matched.iloc[0]

                if district_row is None and market_context.district_name:
                    d_clean = market_context.district_name.strip().upper()
                    matched = self._dataset_df[
                        self._dataset_df["district_name"].str.upper() == d_clean
                    ]
                    if not matched.empty:
                        district_row = matched.iloc[0]

            # 2. If row not found in preloaded set, compute online prediction
            if district_row is not None:
                cluster_id = int(district_row["cluster_id"])
                total_msmes = int(district_row["total_msmes"])
                micro_enterprises = int(district_row["micro_enterprises"])
                small_enterprises = int(district_row["small_enterprises"])
                medium_enterprises = int(district_row["medium_enterprises"])
                micro_share = float(district_row["micro_share"])
                small_share = float(district_row["small_share"])
                medium_share = float(district_row["medium_share"])
                sme_share = float(district_row["small_medium_share"])
                nat_rank = int(district_row["national_rank"])
                st_rank = int(district_row["state_rank"])
                tot_dist_st = int(district_row["total_districts_in_state"])
            elif market_context:
                total_msmes = int(market_context.total_msmes)
                micro_enterprises = int(market_context.micro_enterprises)
                small_enterprises = int(market_context.small_enterprises)
                medium_enterprises = int(market_context.medium_enterprises)
                micro_share = float(market_context.micro_share)
                small_share = float(market_context.small_share)
                medium_share = float(market_context.medium_share)
                sme_share = float(market_context.small_medium_share)
                nat_rank = int(market_context.national_rank or 393)
                st_rank = int(market_context.state_rank or 15)
                tot_dist_st = int(market_context.total_districts_in_state or 30)

                # Online inference
                feature_vals = np.array([[
                    total_msmes,
                    micro_enterprises,
                    small_enterprises,
                    medium_enterprises,
                    micro_share,
                    sme_share,
                ]])
                X_scaled = self.scaler.transform(feature_vals)
                cluster_id = int(self.model.predict(X_scaled)[0])
            else:
                return self._build_fallback_analysis(market_context)

            # 3. Calculate Normalized Percentiles & Market Research Indicator
            nat_density_pct = round(((785 - nat_rank + 1) / 785) * 100.0, 1)
            st_density_pct = round(((tot_dist_st - st_rank + 1) / tot_dist_st) * 100.0, 1)
            # Normalized formalization depth (capped at 10% SME share = 100.0 score)
            sme_depth_score = round(min(sme_share / 10.0, 1.0) * 100.0, 1)

            market_research_indicator = round(
                (WEIGHT_NATIONAL_DENSITY * nat_density_pct)
                + (WEIGHT_STATE_DENSITY * st_density_pct)
                + (WEIGHT_SME_DEPTH * sme_depth_score),
                1,
            )

            cluster_label, cluster_desc = self._cluster_labels_map.get(
                cluster_id, ("Classified Market Cluster", "Empirically grouped district market archetype.")
            )

            means = self._cluster_means.get(
                cluster_id,
                {
                    "mean_total_msmes": float(total_msmes),
                    "mean_micro_share": float(micro_share),
                    "mean_sme_share": float(sme_share),
                },
            )

            indicators = ClusterQuantitativeIndicators(
                total_msmes=total_msmes,
                micro_enterprises=micro_enterprises,
                small_enterprises=small_enterprises,
                medium_enterprises=medium_enterprises,
                micro_share=micro_share,
                small_share=small_share,
                medium_share=medium_share,
                small_medium_share=sme_share,
                national_density_percentile=nat_density_pct,
                state_density_percentile=st_density_pct,
                sme_depth_score=sme_depth_score,
                market_research_indicator=market_research_indicator,
                cluster_mean_total_msmes=round(means["mean_total_msmes"], 1),
                cluster_mean_micro_share=round(means["mean_micro_share"], 2),
                cluster_mean_sme_share=round(means["mean_sme_share"], 2),
            )

            methodology_notes = [
                "Clustering Model: scikit-learn KMeans (K=4, random_state=42, n_init=10) on cross-sectional Udyam records.",
                f"Features normalized via StandardScaler: {', '.join(ML_FEATURES)}.",
                (
                    f"Market Research Indicator: Weighted composite score (0-100) = "
                    f"{int(WEIGHT_NATIONAL_DENSITY*100)}% National Density + "
                    f"{int(WEIGHT_STATE_DENSITY*100)}% State Density + "
                    f"{int(WEIGHT_SME_DEPTH*100)}% Formal SME Depth."
                ),
                "Indicator reflects relative enterprise density and commercial ecosystem scale; does not guarantee individual business success.",
            ]

            return MarketResearchMLAnalysis(
                is_available=True,
                cluster_id=cluster_id,
                cluster_label=cluster_label,
                cluster_description=cluster_desc,
                features_used=ML_FEATURES,
                quantitative_indicators=indicators,
                cluster_distribution_summary=self._cluster_distribution,
                methodology_notes=methodology_notes,
            )
        except Exception as e:
            logger.error("Error evaluating district ML analysis: %s", e, exc_info=True)
            return self._build_fallback_analysis(market_context)

    def _build_fallback_analysis(
        self, market_context: Optional[DistrictMarketContext] = None
    ) -> MarketResearchMLAnalysis:
        """Safe fallback ML analysis object in case of pipeline failure."""
        tot = int(market_context.total_msmes) if market_context else 0
        mic_s = float(market_context.micro_share) if market_context else 0.0
        sme_s = float(market_context.small_medium_share) if market_context else 0.0

        return MarketResearchMLAnalysis(
            is_available=False,
            cluster_id=-1,
            cluster_label="Unclassified Market (ML Fallback)",
            cluster_description="Statistical clustering pipeline is temporarily uninitialized or offline.",
            features_used=ML_FEATURES,
            quantitative_indicators=ClusterQuantitativeIndicators(
                total_msmes=tot,
                micro_enterprises=int(market_context.micro_enterprises) if market_context else 0,
                small_enterprises=int(market_context.small_enterprises) if market_context else 0,
                medium_enterprises=int(market_context.medium_enterprises) if market_context else 0,
                micro_share=mic_s,
                small_share=float(market_context.small_share) if market_context else 0.0,
                medium_share=float(market_context.medium_share) if market_context else 0.0,
                small_medium_share=sme_s,
                national_density_percentile=50.0,
                state_density_percentile=50.0,
                sme_depth_score=round(min(sme_s / 10.0, 1.0) * 100.0, 1),
                market_research_indicator=50.0,
                cluster_mean_total_msmes=float(tot),
                cluster_mean_micro_share=mic_s,
                cluster_mean_sme_share=sme_s,
            ),
            cluster_distribution_summary={},
            methodology_notes=[
                "ML service fallback: Serving basic quantitative aggregates directly from PostgreSQL records."
            ],
        )


# Singleton Instance
market_research_ml_service = MarketResearchMLService()
