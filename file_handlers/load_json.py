import pandas as pd

def load_json(path: str, **kwargs) -> pd.DataFrame:
    """
    Load a JSON file into a DataFrame.
    
    Parameters:
    - path: str | Path to JSON file
    - kwargs: extra params passed to pd.read_json
    
    Returns:
    - pd.DataFrame
    """
    return pd.read_json(path, **kwargs)