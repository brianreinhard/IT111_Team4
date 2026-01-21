from flask import Flask

app = Flask(__name__)

# App metadata
APP_NAME = "Productivity Web App"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "A basic Flask-based application for organizaing and managing information"

@app.route("/")
def home():
    return f"{APP_NAME} is running! (V{APP_VERSION}) - {APP_DESCRIPTION}"

if __name__ == "__main__":
    app.run(debug=True)