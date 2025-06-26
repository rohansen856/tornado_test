import tornado.web
from services.s3 import s3_client, BUCKET_NAME

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
