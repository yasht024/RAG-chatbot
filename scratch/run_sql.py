import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from infra.environments.config import config

def main():
    engine = create_engine(config.postgres_uri)
    query = text("""
    SELECT
        scheme_id,
        COUNT(*) AS chunk_count
    FROM passages
    GROUP BY scheme_id
    ORDER BY scheme_id;
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            print("scheme_id | chunk_count")
            print("-" * 30)
            for row in result:
                # `scheme_ids` is actually a JSON column in Postgres based on models.py
                # but the query uses `scheme_id`. Wait, models.py says `scheme_ids` is JSON, 
                # but the user query has `scheme_id`. 
                # Let's just execute the user query as is and see if it fails.
                print(f"{row[0]} | {row[1]}")
    except Exception as e:
        print(f"Error executing query: {e}")

if __name__ == "__main__":
    main()
