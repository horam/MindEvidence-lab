import json, sys
from .main import app

json.dump(app.openapi(), open(sys.argv[1] if len(sys.argv) > 1 else "openapi.json", "w"), indent=2)
