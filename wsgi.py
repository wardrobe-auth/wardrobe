import os

from wardrobe.webapp import create_app

app = create_app(os.environ.get("FLASK_CONFIG", "default"))
