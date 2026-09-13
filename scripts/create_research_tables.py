"""
scripts/create_research_tables.py

Non-destructive DDL migration for Phase 4A & 4B Research Intelligence layer:
1. district_geo_centroids: Stores geographic coordinates and elevation for 785 LGD districts.
2. district_weather_cache: Stores daily/hourly weather and climate snapshots with TTL.

Invariants:
- PostgreSQL goi_schemes is authoritative.
- Idempotent (CREATE TABLE IF NOT EXISTS).
- Fully transactional.
- Leaves existing tables (districts, states, schemes, programs) 100% untouched.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def get_engine():
    from app.db.database import engine
    return engine


def run_ddl():
    engine = get_engine()

    ddl_statements = [
        # 1. district_geo_centroids table
        """
        CREATE TABLE IF NOT EXISTS district_geo_centroids (
            id SERIAL PRIMARY KEY,
            district_id INT UNIQUE NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
            latitude NUMERIC(9, 6) NOT NULL,
            longitude NUMERIC(9, 6) NOT NULL,
            elevation_meters NUMERIC(7, 2),
            source VARCHAR(50) NOT NULL DEFAULT 'open-meteo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # Index on district_id for fast coordinate lookup
        """
        CREATE INDEX IF NOT EXISTS ix_district_geo_centroids_district_id 
        ON district_geo_centroids(district_id);
        """,

        # 2. district_weather_cache table
        """
        CREATE TABLE IF NOT EXISTS district_weather_cache (
            id SERIAL PRIMARY KEY,
            district_id INT NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
            cache_type VARCHAR(20) NOT NULL DEFAULT 'FORECAST',
            observation_date DATE NOT NULL,
            current_metrics JSONB,
            daily_forecast JSONB,
            source VARCHAR(50) NOT NULL DEFAULT 'open-meteo',
            fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            is_stale BOOLEAN NOT NULL DEFAULT FALSE,
            CONSTRAINT uq_district_weather_cache UNIQUE (district_id, observation_date, cache_type)
        );
        """,

        # Index on lookup fields
        """
        CREATE INDEX IF NOT EXISTS ix_district_weather_cache_lookup 
        ON district_weather_cache(district_id, observation_date, cache_type);
        """
    ]

    print("Executing Phase 4A & 4B DDL non-destructively in a single transaction...")
    with engine.begin() as conn:
        for stmt in ddl_statements:
            conn.execute(text(stmt))

    print("Phase 4A & 4B DDL executed successfully.")


if __name__ == "__main__":
    run_ddl()
