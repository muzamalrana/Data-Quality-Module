import pandas as pd

def load_parquet(path: str, **kwargs) -> pd.DataFrame:
    """
    Load a Parquet file into a DataFrame.
    
    Parameters:
    - path: str | Path to Parquet file
    - kwargs: extra params passed to pd.read_parquet
    
    Returns:
    - pd.DataFrame
    """
    return pd.read_parquet(path, **kwargs)
