import os

def detect_file_type(file_path: str) -> str:
    """
    Detects the type of a file based on its extension.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: File type (e.g., 'csv', 'excel', 'json', 'parquet', 'text', 'xml', 'tsv', 'zip', 'gzip', 'unknown').
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ['.csv']:
        return 'csv'
    elif ext in ['.xls', '.xlsx']:
        return 'excel'
    elif ext in ['.json']:
        return 'json'
    elif ext in ['.parquet']:
        return 'parquet'
    elif ext in ['.txt']:
        return 'text'
    elif ext in ['.xml']:
        return 'xml'
    elif ext in ['.tsv']:
        return 'tsv'
    elif ext in ['.zip']:
        return 'zip'
    elif ext in ['.gz', '.gzip']:
        return 'gzip'
    else:
        return 'unknown'
