import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import urllib
import getpass
# Caches
_engine = None
_cached_query = {}

def load_sql_server_data(args,**kwagrs):
    global _engine, _cached_query

    # Step 1: Create engine only on first run
    if _engine is None:
        host = getpass.getpass("Enter SQL Server host/IP: ").strip()
        port = getpass.getpass("Enter port (default 1433): ").strip() or "1433"
        database = getpass.getpass("Enter SQL Server database name: ").strip()

        server = f"{host},{port}"
        conn_str = (
            "Driver={ODBC Driver 17 for SQL Server};"
            f"Server={server};"
            f"Database={database};"
            "Trusted_Connection=yes;"
        )
        conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(
            urllib.parse.quote_plus(conn_str)
        )
        _engine = create_engine(conn_str)
    else:
        print("✅ Reusing existing SQL Server engine...")

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

        print("✅ Data loaded successfully from SQL Server.")
        return df

    except Exception as e:
        print(f"❌ Error loading data from SQL Server: {e}")
        return None
