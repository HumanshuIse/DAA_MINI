from pathlib import Path
from flask import Flask, jsonify, render_template

from database.db import Database
from routes.api_routes import api


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(DB=Database(Path(app.instance_path) / "arena.sqlite3"))
    if test_config:
        app.config.update(test_config)
    app.config["DB"].connect().close()
    app.register_blueprint(api)

    @app.errorhandler(ValueError)
    def bad_request(error):
        return jsonify({"error": str(error)}), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Unexpected server error"}), 500

    @app.get("/")
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
