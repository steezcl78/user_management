from minio import Minio
from minio.error import S3Error


def main():
   # Create a client with the MinIO server playground, its access key
   # and secret key.
   client = Minio(
       "localhost:9000",
       access_key="u66x9tZKzLWXwd96YHbZ",
       secret_key="2D6K04vua6D07w2y2ejPymwLy4CVrwow2mVtay9d",
       secure=False,
   )

   # Make 'demo' bucket if not exist.
   found = client.bucket_exists("profilephotos")
   if not found:
       client.make_bucket("profilephotos")
   else:
       print("Bucket 'profilephotos' already exists")

   # Upload 'minio.jpg' as object name
   # 'minio.jpg' to bucket 'demo'.
   client.fput_object(
       "profilephotos",
       "IMG_0490.HEIC",
       "/Users/christianlee/Downloads/IMG_0490.HEIC"
   )
   print(
       "'IMG_0490.HEIC' is successfully uploaded as "
       "object 'img_0490.heic' to bucket 'profilephotos'."
   )


if __name__ == "__main__":
   try:
       main()
   except S3Error as exc:
       print("error occurred.", exc)