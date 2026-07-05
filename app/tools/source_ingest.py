import os

def ingest_source(source_path: str) -> dict:
    """
    Given a URL, handle, PDF, or local file, return the extracted text.
    For v1, URL, social handles, and PDF are explicitly gracefully declined.
    Only local markdown/text files are processed.
    """
    source_path = source_path.strip()
    
    if source_path.startswith("http://") or source_path.startswith("https://"):
        return {
            "status": "unsupported",
            "message": f"URL ingestion is out of scope for v1: {source_path}"
        }
    
    if source_path.startswith("@"):
        return {
            "status": "unsupported",
            "message": f"Social handle ingestion is out of scope for v1: {source_path}"
        }
        
    if source_path.lower().endswith(".pdf"):
        return {
            "status": "unsupported",
            "message": f"PDF ingestion is out of scope for v1: {source_path}"
        }
        
    if not os.path.exists(source_path):
        return {
            "status": "failed",
            "message": f"File not found: {source_path}"
        }
        
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return {
                "status": "success",
                "text": content,
                "message": f"Successfully ingested {source_path}"
            }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Error reading file {source_path}: {str(e)}"
        }
