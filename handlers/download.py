import tornado.web
from services.s3 import s3_client, BUCKET_NAME

class FileDownloadHandler(tornado.web.RequestHandler):
    def get(self, file_key):
        try:
            response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)

            self.set_header('Content-Type', response['ContentType'])
            self.set_header('Content-Disposition', f'attachment; filename="{file_key.split('-', 1)[1]}"')
            self.write(response['Body'].read())
        except Exception as e:
            self.set_status(500)
            self.write({"error": str(e)})
