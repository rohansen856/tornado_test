import psycopg2
from psycopg2.extras import RealDictCursor
import os

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "test"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432")
)

cursor = conn.cursor(cursor_factory=RealDictCursor)
