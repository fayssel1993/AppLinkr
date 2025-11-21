from flask import Flask
import os
from config import get_database_location
from db import close_db
from routes import setup_routes

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database setup
# Define the database location, falling back to a writable directory when needed
DATABASE_FOLDER, DATABASE_PATH = get_database_location()

# GET ENVS
SERVER_URL = os.getenv("SERVER_URL")
PASSWORD = os.getenv("PASSWORD")

# Register the database teardown function
@app.teardown_appcontext
def teardown(exception):
    close_db(exception)

# Set up routes
setup_routes(app, SERVER_URL, PASSWORD)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
