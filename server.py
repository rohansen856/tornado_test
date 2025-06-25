import tornado.ioloop
import tornado.web
import json

# Helper: Input validation
def validate_input(data, required_fields):
    missing = [field for field in required_fields if field not in data]
    if missing:
        return False, f"Missing fields: {', '.join(missing)}"
    return True, None

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class EchoHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            data = json.loads(self.request.body)
            self.write({"you_sent": data})
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Invalid JSON"})

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/echo", EchoHandler),
    ], template_path="templates")

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Server running on http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
