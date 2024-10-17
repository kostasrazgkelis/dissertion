import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_client = None

def init_app(app):
    """
    Initialize the MongoDB connection using MongoClient.
    """
    mongo_uri = os.getenv('MONGO_URI')
    
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in the environment variables.")
    
    global mongo_client
    mongo_client = MongoClient(mongo_uri)

    # Access a specific database if needed
    app.mongo_db = mongo_client.get_database("mydatabase")

    # Optional: If you want to create a collection
    create_collections(app.mongo_db)

def create_collections(db):
    """
    Create the necessary collections if they do not exist.
    """
    # Create 'users' collection if it doesn't exist
    if 'users' not in db.list_collection_names():
        db.create_collection('users')
