import tornado.web
import uuid
from services.s3 import s3_client, BUCKET_NAME
from services.database import cursor, conn

class FileUploadHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            file_info = self.request.files['file'][0]
            file_name = file_info['filename']
            file_body = file_info['body']
            content_type = file_info['content_type']

            unique_filename = f"{uuid.uuid4()}-{file_name}"

            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=unique_filename,
                Body=file_body,
                ContentType=content_type
            )

            user_id = self.get_argument('user_id', None)
            if user_id:
                cursor.execute(
                    "INSERT INTO user_files (user_id, filename, s3_key) VALUES (%s, %s, %s) RETURNING id",
                    (user_id, file_name, unique_filename)
                )
                conn.commit()

            self.redirect("/storage")
        except Exception as e:
            conn.rollback()
            self.set_status(500)
            self.write({"error": str(e)})
