import pandas as pd

def load_excel(path: str, sheet_name: str = None, **kwargs) -> pd.DataFrame:
    """
    Load an Excel file into a DataFrame.
    
    Parameters:
    - path: str | Path to Excel file
    - sheet_name: str | Sheet to load, defaults to first sheet
    - kwargs: extra params passed to pd.read_excel
    
    Returns:
    - pd.DataFrame
    """
    df=pd.read_excel(path, sheet_name=sheet_name, **kwargs)
    return df