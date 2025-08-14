import zipfile
import pandas as pd
from io import BytesIO

def load_compressed(path: str, file_inside: str = None, **kwargs) -> pd.DataFrame:
    """
    Load a file inside a compressed archive (zip) into a DataFrame.
    
    Parameters:
    - path: str | Path to zip archive
    - file_inside: str | Filename inside zip to load (required if multiple files)
    - kwargs: extra params passed to specific loaders
    
    Returns:
    - pd.DataFrame
    """
    with zipfile.ZipFile(path, 'r') as z:
        # If no filename specified, try to pick the first file
        if not file_inside:
            file_inside = z.namelist()[0]
        with z.open(file_inside) as f:
            # Infer file extension to decide how to load
            ext = file_inside.split('.')[-1].lower()
            if ext == 'csv':
                return pd.read_csv(f, **kwargs)
            elif ext in ['xls', 'xlsx']:
                return pd.read_excel(f, **kwargs)
            elif ext == 'json':
                return pd.read_json(f, **kwargs)
            elif ext == 'parquet':
                return pd.read_parquet(f, **kwargs)
            else:
                raise ValueError(f"Unsupported file type {ext} inside zip")
