from .sql_loader import load_sql_server_data
from .postgres_loader import load_postgres_data

def load_from_database(db_type='sqlserver'):
    """
    Universal database loader that dispatches to the appropriate DB handler.
    
    Args:
        db_type (str): Type of the database ('sqlserver', 'postgres')
        **kwargs: Connection parameters and query details:
            Required keys typically include:
                - server / host
                - port (for Postgres)
                - database
                - username (if needed)
                - password (if needed)
                - trusted_connection (for SQL Server)
                - query or table_name

    Returns:
        pd.DataFrame: Loaded data as a DataFrame.
    """
    db_type = db_type.lower()
    
    if db_type == "sqlserver":
        return load_sql_server_data()
    elif db_type == "postgres":
        return load_postgres_data()
    else:
        raise ValueError(f"❌ Unsupported database type: {db_type}")
