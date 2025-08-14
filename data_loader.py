import os
import pandas as pd
from pathlib import Path

# Import file handlers
from file_handlers.load_csv import load_csv
from file_handlers.load_excel import load_excel
from file_handlers.load_json import load_json
from file_handlers.load_parquet import load_parquet
from file_handlers.load_txt import load_txt
from file_handlers.load_xml import load_xml
from file_handlers.load_compressed import load_compressed

# Import DB & Web handlers
from db_handlers.sql_loader import load_sql_server_data
from db_handlers.postgres_loader import load_postgres_data

# Utility
from utils.logger import logger
from utils.file_detector import detect_file_type


def load_data(source: str = None, source_type: str = None, **kwargs) -> pd.DataFrame:
    """
    Main function to load data from any source.
    
    Parameters:
    - source: str | URL, file path, SQL query, or API endpoint
    - source_type: str | Explicit type like 'csv', 'sql', 'api' (optional)
    - kwargs: dict | Extra arguments passed to specific loaders
    
    Returns:
    - DataFrame
    """
    logger.info(f" Loading data from source: {source}")

    # Auto-detect if type is not passed
    try:
        print(source_type)
        source_type=source_type.strip().lower()
        print(source_type)
    except:
        pass
    if not source_type:
        source_type = detect_file_type(source)
        logger.info(f" Auto-detected source type: {source_type}")
   
    loaders = {
        'csv': load_csv,
        'excel': load_excel,
        'json': load_json,
        'parquet': load_parquet,
        'txt': load_txt,
        'xml': load_xml,
        'zip': load_compressed,
        'sqlserver': load_sql_server_data,
        'postgres': load_postgres_data
    }
    
    loader_func = loaders.get(source_type)
    if not loader_func:
        raise ValueError(f" Unsupported source_type: {source_type}")

    try:
        df = loader_func(source, **kwargs)
        logger.info(f"Loaded data successfully. Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f" Failed to load data using {source_type} loader: {e}")
        raise
