import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import getpass

# Caches
_engine = None
_cached_query = {}

def load_postgres_data(args,**kwagrs):
    global _engine, _cached_query

    # Step 1: Create engine only on first run
    if _engine is None:
        username = getpass.getpass("Enter PostgreSQL username: ")
        password = getpass.getpass("Enter PostgreSQL password: ")
        host = getpass.getpass("Enter PostgreSQL host (e.g., 127.0.0.1): ")
        port = getpass.getpass("Enter PostgreSQL port (default 5432): ") or "5432"
        database = input("Enter PostgreSQL database name: ")

        encoded_password = quote_plus(password)
        connection_str = f"postgresql+psycopg2://{username}:{encoded_password}@{host}:{port}/{database}"
        _engine = create_engine(connection_str)
    else:
        print("✅ Reusing existing engine...")

    # Step 2: Use cached query or prompt on first run
    if not _cached_query:
        table = input("Enter SQL table (leave blank to enter custom query): ").strip()
        if table:
            _cached_query["mode"] = "table"
            _cached_query["value"] = table
        else:
            query = input("Enter SQL query: ").strip()
            _cached_query["mode"] = "query"
            _cached_query["value"] = query
    else:
        print("✅ Reusing previous table/query...")

    # Step 3: Load data
    try:
        if _cached_query["mode"] == "table":
            df = pd.read_sql_table(_cached_query["value"], _engine)
        else:
            df = pd.read_sql_query(_cached_query["value"], _engine)

        print("✅ Data loaded successfully.")
        return df

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None
