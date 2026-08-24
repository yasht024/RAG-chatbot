import json
import os
import sys

# Add the project root to python path so we can import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.assistant_api.main import app
from fastapi.openapi.utils import get_openapi

def export():
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    
    out_dir = os.path.join(os.path.dirname(__file__), "..", "docs", "schemas")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "openapi.json")
    
    with open(out_path, "w") as f:
        json.dump(openapi_schema, f, indent=2)
        
    print(f"Exported OpenAPI schema to {out_path}")

if __name__ == "__main__":
    export()
