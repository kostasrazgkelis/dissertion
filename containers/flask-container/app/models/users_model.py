# app/models.py
from bson import ObjectId
from db import mongo_client as mongo
from uuid import UUID
from config import logger

class User:
    @staticmethod
    async def create_user(data):
        try:
            user_id = await mongo.db.users.insert_one(data).inserted_id
            logger.info(f"User created with ID: {user_id}")
            return str(user_id)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    @staticmethod
    async def get_user(user_id):
        try:
            user = await mongo.db.users.find_one({"_id": UUID(user_id)})
            logger.info(f"User: {user}")
            return user if user else None
        except Exception as e:
            logger.error(f"Error retrieving user: {e}")
            return None

    @staticmethod
    def update_user(user_id, data):
        result = mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": data})
        return result

    @staticmethod
    def delete_user(user_id):
        result = mongo.db.users.find_one_and_delete({"_id": user_id})
        return result

    @staticmethod
    def get_all_users():
        users_cursor = mongo.db.users.find()  # MongoDB cursor
        users = list(users_cursor)  # Convert cursor to list
        for user in users:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
        return users