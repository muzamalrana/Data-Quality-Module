from .load_csv import load_csv
from .load_excel import load_excel
from .load_json import load_json
from .load_parquet import load_parquet
from .load_txt import load_txt
from .load_xml import load_xml
from .load_compressed import load_compressed

def load_file(file_path: str, file_type: str = None, **kwargs):
    """
    Universal file loader that delegates to the appropriate handler based on file type or extension.
    
    Args:
        file_path (str): Path to the input file.
        file_type (str): Optional explicit type (e.g., 'csv', 'excel', 'json', etc.)
        **kwargs: Additional parameters for specific loaders (e.g., encoding, sheet_name).

    Returns:
        pd.DataFrame: Loaded data as a DataFrame.
    """
    # Auto-detect file type if not provided
    if not file_type:
        if file_path.endswith(".csv"):
            file_type = "csv"
        elif file_path.endswith((".xls", ".xlsx")):
            file_type = "excel"
        elif file_path.endswith(".json"):
            file_type = "json"
        elif file_path.endswith(".parquet"):
            file_type = "parquet"
        elif file_path.endswith((".txt", ".tsv")):
            file_type = "text"
        elif file_path.endswith(".xml"):
            file_type = "xml"
        elif file_path.endswith((".zip", ".gz", ".tar", ".rar")):
            file_type = "compressed"
        else:
            raise ValueError("❌ Cannot detect file type. Please specify `file_type` manually.")

    # Dispatch to specific loader
    if file_type == "csv":
        return load_csv(file_path, **kwargs)
    elif file_type == "excel":
        return load_excel(file_path, **kwargs)
    elif file_type == "json":
        return load_json(file_path, **kwargs)
    elif file_type == "parquet":
        return load_parquet(file_path, **kwargs)
    elif file_type == "text" or file_type == "tsv":
        return load_text(file_path, **kwargs)
    elif file_type == "xml":
        return load_xml(file_path, **kwargs)
    elif file_type == "compressed":
        return load_compressed(file_path, **kwargs)
    else:
        raise ValueError(f"❌ Unsupported file type: {file_type}")
