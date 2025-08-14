import pandas as pd

def load_txt(path: str, delimiter: str = '\t', **kwargs) -> pd.DataFrame:
    """
    Load a delimited text file into a DataFrame.
    
    Parameters:
    - path: str | Path to the text file
    - delimiter: str | Field delimiter, default tab
    
    Returns:
    - pd.DataFrame
    """
    return pd.read_csv(path, delimiter=delimiter, **kwargs)
