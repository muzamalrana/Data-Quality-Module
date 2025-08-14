import pandas as pd

def load_csv(path: str, **kwargs) -> pd.DataFrame:
    """
    Load a CSV file into a DataFrame.
    
    Parameters:
    - path: str | Path to the CSV file
    - kwargs: extra params passed to pd.read_csv
    
    Returns:
    - pd.DataFrame
    """
    return pd.read_csv(path, **kwargs)