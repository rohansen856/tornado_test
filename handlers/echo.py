import tornado.web
import json

class EchoHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            data = json.loads(self.request.body)
            self.write({"you_sent": data})
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON"})
