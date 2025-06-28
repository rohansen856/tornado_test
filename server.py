from handlers.htmltopdf import PdfConverterHandler
import tornado.ioloop
import tornado.web
from handlers.main import MainHandler
from handlers.user import UserHandler
from handlers.storage import StorageHandler
from handlers.upload import FileUploadHandler
from handlers.delete import FileDeleteHandler
from handlers.download import FileDownloadHandler
from handlers.echo import EchoHandler
from services.database import cursor, conn
from services.s3 import ensure_bucket_exists

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/echo", EchoHandler),
        (r"/users", UserHandler),
        (r"/storage", StorageHandler),
        (r"/upload", FileUploadHandler),
        (r"/delete", FileDeleteHandler),
        (r"/download/(.*)", FileDownloadHandler),
        (r"/convert-to-pdf", PdfConverterHandler),
    ], template_path="templates")

if __name__ == "__main__":
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

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
