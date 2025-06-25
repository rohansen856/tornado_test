import tornado.ioloop
import tornado.web
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import os

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME") if os.getenv("DB_NAME") else "test",
    user=os.getenv("DB_USER") if os.getenv("DB_USER") else "postgres",
    password=os.getenv("DB_PASSWORD") if os.getenv("DB_PASSWORD") else "postgres",
    host=os.getenv("DB_HOST") if os.getenv("DB_HOST") else "localhost",
    port=os.getenv("DB_PORT") if os.getenv("DB_PORT") else "5432"
)
cursor = conn.cursor(cursor_factory=RealDictCursor)

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
    ], template_path="templates")

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Server running on http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
