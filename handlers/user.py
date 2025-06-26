import tornado.web
import json
from services.database import cursor, conn
from utils.validators import validate_input

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
