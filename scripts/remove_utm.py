import json
from pathlib import Path
from urllib.parse import urlparse, urlunparse

def strip_query_params():
    root_dir = Path(__file__).parents[1]
    schemes_path = root_dir / "data" / "catalog" / "schemes.json"
    
    with open(schemes_path, "r", encoding="utf-8") as f:
        schemes = json.load(f)
        
    for scheme in schemes:
        url = scheme["groww_url"]
        
        # Parse the URL and remove the query parameters
        url_parts = list(urlparse(url))
        url_parts[4] = '' # Remove query parameters
        new_url = urlunparse(url_parts)
        
        scheme["groww_url"] = new_url
                
    with open(schemes_path, "w", encoding="utf-8") as f:
        json.dump(schemes, f, indent=2)
        
    print(f"Stripped query parameters from {len(schemes)} URLs")

if __name__ == "__main__":
    strip_query_params()
