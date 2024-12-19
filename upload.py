from minio import Minio
from minio.error import S3Error


def main():
   # Create a client with the MinIO server playground, its access key
   # and secret key.
   client = Minio(
       "minio:9000",
       access_key="u66x9tZKzLWXwd96YHbZ",
       secret_key="2D6K04vua6D07w2y2ejPymwLy4CVrwow2mVtay9d",
       secure=False,
   )

   # Make 'demo' bucket if not exist.
   found = client.bucket_exists("demo")
   if not found:
       client.make_bucket("demo")
   else:
       print("Bucket 'demo' already exists")

   # Upload 'minio.jpg' as object name
   # 'minio.jpg' to bucket 'demo'.
   client.fput_object(
       "profilephotos",
       "minio.jpg",
       "./minio.jpg",
   )
   print(
       "'minio.jpg' is successfully uploaded as "
       "object 'minio.jpg' to bucket 'demo'."
   )


if __name__ == "__main__":
   try:
       main()
   except S3Error as exc:
       print("error occurred.", exc)