import tornado.ioloop
import tornado.web
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import boto3
from botocore.exceptions import ClientError
import uuid

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME") if os.getenv("DB_NAME") else "test",
    user=os.getenv("DB_USER") if os.getenv("DB_USER") else "postgres",
    password=os.getenv("DB_PASSWORD") if os.getenv("DB_PASSWORD") else "postgres",
    host=os.getenv("DB_HOST") if os.getenv("DB_HOST") else "localhost",
    port=os.getenv("DB_PORT") if os.getenv("DB_PORT") else "5432"
)
cursor = conn.cursor(cursor_factory=RealDictCursor)

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)
BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'my-tornado-bucket')

def ensure_bucket_exists():
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        else:
            raise

def validate_input(data, required_fields):
    missing = [field for field in required_fields if field not in data]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    return True, None

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class StorageHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
            files = []
            if 'Contents' in response:
                files = [
                    {
                        'key': item['Key'],
                        'size': item['Size'],
                        'last_modified': item['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                    }
                    for item in response['Contents']
                ]
            self.render("storage.html", files=files)
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})

class FileUploadHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            file_info = self.request.files['file'][0]
            file_name = file_info['filename']
            file_body = file_info['body']
            file_content_type = file_info['content_type']
            
            unique_filename = f"{uuid.uuid4()}-{file_name}"
            
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=unique_filename,
                Body=file_body,
                ContentType=file_content_type
            )
            
            user_id = self.get_argument('user_id', None)
            if user_id:
                cursor.execute(
                    "INSERT INTO user_files (user_id, filename, s3_key) VALUES (%s, %s, %s) RETURNING id", 
                    (user_id, file_name, unique_filename)
                )
                file_id = cursor.fetchone()["id"]
                conn.commit()
                
            self.redirect("/storage")
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})

class FileDeleteHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            file_key = self.get_argument('key')
            
            s3_client.delete_object(
                Bucket=BUCKET_NAME,
                Key=file_key
            )
            
            cursor.execute("DELETE FROM user_files WHERE s3_key = %s", (file_key,))
            conn.commit()
            
            self.redirect("/storage")
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})

class FileDownloadHandler(tornado.web.RequestHandler):
    def get(self, file_key):
        try:
            response = s3_client.get_object(
                Bucket=BUCKET_NAME,
                Key=file_key
            )
            
            self.set_header('Content-Type', response['ContentType'])
            self.set_header('Content-Disposition', f'attachment; filename="{file_key.split("-", 1)[1]}"')
            
            self.write(response['Body'].read())
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})

class EchoHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            data = json.loads(self.request.body)
            self.write({"you_sent": data})
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON"})

class UserHandler(tornado.web.RequestHandler):
    def get(self):
        cursor.execute("SELECT id, name, email FROM users")
        users = cursor.fetchall()
        self.write({"users": users})

    def post(self):
        try:
            data = json.loads(self.request.body)
            valid, error = validate_input(data, ["name", "email"])
            if not valid:
                self.set_status(400)
                self.write({"error": error})
                return

            cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id", (data["name"], data["email"]))
            user_id = cursor.fetchone()["id"]
            conn.commit()
            self.write({"id": user_id, "message": "User created"})
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})

    def put(self):
        try:
            data = json.loads(self.request.body)
            valid, error = validate_input(data, ["id", "name", "email"])
            if not valid:
                self.set_status(400)
                self.write({"error": error})
                return

            cursor.execute("UPDATE users SET name=%s, email=%s WHERE id=%s", (data["name"], data["email"], data["id"]))
            conn.commit()
            self.write({"message": "User updated"})
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/echo", EchoHandler),
        (r"/users", UserHandler),
        (r"/storage", StorageHandler),
        (r"/upload", FileUploadHandler),
        (r"/delete", FileDeleteHandler),
        (r"/download/(.*)", FileDownloadHandler),
    ], template_path="templates")

if __name__ == "__main__":
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_files (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        filename TEXT NOT NULL,
        s3_key TEXT NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    
    ensure_bucket_exists()
    
    app = make_app()
    app.listen(8888)
    print("Server running on http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()