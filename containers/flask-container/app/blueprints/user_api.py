# app/blueprints/user_api.py
import uuid
from flask import Blueprint, request, jsonify, make_response
from config import UPLOAD_FOLDER
from werkzeug.utils import secure_filename
import os
from serializers.users import user_schema, users_schema
from marshmallow import ValidationError
from config import logger

user_api = Blueprint('user_api', __name__)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@user_api.route('/api/v1/users', methods=['POST'])
def create_user():
    from models.users_model import User

    data = request.form.to_dict() 
    files = request.files.getlist('files')

    try:
        validated_data = user_schema.load(data)
    except ValidationError as err:
        return make_response(jsonify(err.messages), 400)
    
    user_id = User.create_user(validated_data)
    
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    os.makedirs(user_folder, exist_ok=True)

    file_metadata_list = []
    if files:
        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(user_folder, filename)  # Save file in user's folder
            file.save(file_path)
            
            # Create file metadata
            file_metadata = {
                "file_name": filename,
                "file_path": file_path,
            }
            file_metadata_list.append(file_metadata)
        
    return make_response(jsonify({"user_id": str(user_id)}), 201)

@user_api.route('/api/v1/users/<user_id>', methods=['GET'])
def get_user(user_id):
    from models.users_model import User

    try:
        user_uuid = uuid.UUID(user_id)  # Convert user_id to UUID
    except ValueError as e:
        logger.error(f"Invalid UUID format: {user_id}")
        return make_response(jsonify({"error": f"Invalid UUID format: {user_id}"}), 400)
    

    user = User.get_user(user_id)

    if user is None:
        return make_response(jsonify({"error": "User not found"}), 404)

    try:
        validated_data = user_schema.load(user)
    except ValidationError as err:
        return make_response(jsonify(err.messages), 400)

    return make_response(jsonify(validated_data), 200)

@user_api.route('/api/v1/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    from models.users_model import User
    
    data = request.get_json()
    if User.update_user(user_id, data):
        return make_response(jsonify({"message": "User updated successfully"}), 200)
    return make_response(jsonify({"error" : f"User {user_id} not found"}), 404)

@user_api.route('/api/v1/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    from models.users_model import User
    try:
        user_uuid = uuid.UUID(user_id)  # Convert user_id to UUID
    except ValueError as e:
        logger.error(f"Invalid UUID format: {user_id}")
        return make_response(jsonify({"error": f"Invalid UUID format: {user_id}"}), 400)

    if User.delete_user(user_id):
        return make_response(jsonify({"message": "User deleted successfully"}), 200)
    return make_response(jsonify({"error" : f"User {user_id} not found"}), 404)

@user_api.route('/api/v1/users', methods=['GET'])
def get_all_users():
    from models.users_model import User

    users = User.get_all_users()

    # try:
    #     validated_data = users_schema.load(users)
    # except ValidationError as err:
    #     return make_response(jsonify(err.messages), 400)

    return jsonify(users), 200
