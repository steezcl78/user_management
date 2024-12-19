import uuid
from unittest.mock import patch, MagicMock
import pytest
from upload import upload_profile_photo  # Adjusted import
from app.models.user_model import User


# Mock configuration
MINIO_ENDPOINT = "localhost:9000"
BUCKET_NAME = "profilephotos"


@pytest.fixture
def mock_minio_client():
    """Fixture for mocking the MinIO client."""
    with patch("upload.client") as mock_client:
        yield mock_client


@pytest.fixture
def mock_database_session():
    """Fixture for mocking the database session."""
    with patch("upload.Database") as mock_db:
        mock_session = MagicMock()
        mock_db.return_value.__enter__.return_value = mock_session
        yield mock_session


def test_upload_profile_photo_success(mock_minio_client, mock_database_session):
    """Test successful profile photo upload."""
    # Mock user ID and file paths
    user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    file_path = "/fake/path/photo.jpg"
    file_name = "photo.jpg"
    mock_user = User(id=user_id, profile_picture_url=None)

    # Mock bucket and upload behavior
    mock_minio_client.bucket_exists.return_value = True
    mock_minio_client.fput_object.return_value = None

    # Mock database query and update
    mock_database_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Call the function
    profile_url = upload_profile_photo(user_id, file_path, file_name)

    # Assertions
    expected_url = f"http://{MINIO_ENDPOINT}/{BUCKET_NAME}/{user_id}/{file_name}"
    assert profile_url == expected_url
    assert mock_user.profile_picture_url == expected_url
    mock_minio_client.bucket_exists.assert_called_once_with(BUCKET_NAME)
    mock_minio_client.fput_object.assert_called_once_with(
        BUCKET_NAME, f"{user_id}/{file_name}", file_path
    )
    mock_database_session.commit.assert_called_once()


def test_upload_profile_photo_user_not_found(mock_minio_client, mock_database_session):
    """Test upload when the user is not found in the database."""
    user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    file_path = "/fake/path/photo.jpg"
    file_name = "photo.jpg"

    # Mock database query
    mock_database_session.query.return_value.filter.return_value.first.return_value = None

    # Expect a ValueError
    with pytest.raises(ValueError, match=f"User with ID {user_id} not found."):
        upload_profile_photo(user_id, file_path, file_name)

    mock_database_session.commit.assert_not_called()


def test_upload_profile_photo_bucket_creation(mock_minio_client, mock_database_session):
    """Test bucket creation if it doesn't exist."""
    user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    file_path = "/fake/path/photo.jpg"
    file_name = "photo.jpg"
    mock_user = User(id=user_id, profile_picture_url=None)

    # Mock bucket creation
    mock_minio_client.bucket_exists.return_value = False
    mock_database_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Call the function
    upload_profile_photo(user_id, file_path, file_name)

    # Assertions
    mock_minio_client.make_bucket.assert_called_once_with(BUCKET_NAME)


def test_upload_profile_photo_s3_error(mock_minio_client, mock_database_session):
    """Test handling of S3 errors during file upload."""
    user_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    file_path = "/fake/path/photo.jpg"
    file_name = "photo.jpg"
    mock_user = User(id=user_id, profile_picture_url=None)

    # Mock S3 error
    mock_minio_client.bucket_exists.return_value = True
    mock_minio_client.fput_object.side_effect = Exception("S3 Upload Failed")
    mock_database_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Expect the upload to raise an exception
    with pytest.raises(Exception, match="S3 Upload Failed"):
        upload_profile_photo(user_id, file_path, file_name)

    mock_database_session.commit.assert_not_called()