import pandas as pd

def load_xml(path: str, **kwargs) -> pd.DataFrame:
    """
    Load XML file into a DataFrame.
    
    Parameters:
    - path: str | Path to XML file
    - kwargs: extra params passed to pd.read_xml (Pandas 1.3+)
    
    Returns:
    - pd.DataFrame
    """
    return pd.read_xml(path, **kwargs)
