import tornado.web
from services.s3 import s3_client, BUCKET_NAME
from services.database import cursor, conn

class FileDeleteHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            file_key = self.get_argument('key')

            s3_client.delete_object(Bucket=BUCKET_NAME, Key=file_key)
            cursor.execute("DELETE FROM user_files WHERE s3_key = %s", (file_key,))
            conn.commit()

            self.redirect("/storage")
        except Exception as e:
            conn.rollback()
            self.set_status(500)
            self.write({"error": str(e)})
