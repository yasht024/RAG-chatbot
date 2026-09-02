import json
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

def update_urls_with_utm():
    root_dir = Path(__file__).parents[1]
    schemes_path = root_dir / "data" / "catalog" / "schemes.json"
    
    with open(schemes_path, "r", encoding="utf-8") as f:
        schemes = json.load(f)
        
    for scheme in schemes:
        url = scheme["groww_url"]
        
        # Parse the URL
        url_parts = list(urlparse(url))
        query = dict(parse_qsl(url_parts[4]))
        
        # Add or update the utm_source
        query['utm_source'] = 'chatgpt.com'
        
        # Reconstruct the URL
        url_parts[4] = urlencode(query)
        new_url = urlunparse(url_parts)
        
        scheme["groww_url"] = new_url
                
    with open(schemes_path, "w", encoding="utf-8") as f:
        json.dump(schemes, f, indent=2)
        
    print(f"Updated {len(schemes)} URLs with utm_source=chatgpt.com")

if __name__ == "__main__":
    update_urls_with_utm()
