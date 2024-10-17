from marshmallow import Schema, fields, post_load
import uuid
from config import logger

class FileMetadataSchema(Schema):
    files_path = fields.Str(required=True)

class UserSchema(Schema):
    id = fields.UUID(attribute="_id", default=uuid.uuid4) 
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    files = fields.List(fields.Nested(FileMetadataSchema))

    @post_load
    def make_user(self, data, **kwargs):
        # Ensure _id is a UUID
        if isinstance(data.get('_id'), str):
            try:
                data['_id'] = uuid.UUID(data['_id'])
            except ValueError as e:
                logger.error(f"Invalid UUID format: {data['_id']}")
                raise e
        return data
    
user_schema = UserSchema()
users_schema = UserSchema(many=True)  # For serializing multiple users
