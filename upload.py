import uuid
from minio import Minio
from minio.error import S3Error
from app.database import Database
from app.models.user_model import User

# MinIO Configuration
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "u66x9tZKzLWXwd96YHbZ"
MINIO_SECRET_KEY = "2D6K04vua6D07w2y2ejPymwLy4CVrwow2mVtay9d"
BUCKET_NAME = "profilephotos"

# Initialize MinIO client
client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False  # Set to True if using HTTPS
)

def upload_profile_photo(user_id: uuid.UUID, file_path: str, file_name: str):
    """
    Uploads a profile photo to MinIO and updates the user's profile_picture_url in the database.

    Args:
        user_id (uuid.UUID): ID of the user whose profile photo is being uploaded.
        file_path (str): Path to the file to upload.
        file_name (str): Name of the file to save in MinIO.

    Returns:
        str: URL of the uploaded profile photo.
    """
    # Ensure the bucket exists
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)

    # Upload the file
    object_name = f"{user_id}/{file_name}"
    try:
        client.fput_object(BUCKET_NAME, object_name, file_path)
        print(f"File uploaded successfully as {object_name}")
    except S3Error as e:
        print(f"Failed to upload file: {e}")
        raise

    # Construct the file URL
    file_url = f"http://{MINIO_ENDPOINT}/{BUCKET_NAME}/{object_name}"

    # Update the user's profile_picture_url in the database
    with Database() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found.")
        user.profile_picture_url = file_url
        session.commit()

    return file_url

def main():
    # Example usage
    user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    file_path = "/Users/christianlee/Downloads/IMG_0490.HEIC"
    file_name = "photo.HEIC"

    try:
        profile_picture_url = upload_profile_photo(user_id, file_path, file_name)
        print(f"Profile picture uploaded successfully: {profile_picture_url}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()