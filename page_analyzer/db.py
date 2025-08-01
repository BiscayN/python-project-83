import os
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import NamedTupleCursor


load_dotenv()


class UrlRepo:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")

    def add_url(self, name):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO urls (name) VALUES (%s) RETURNING id",
                    (name,)
                )
                url_id = cursor.fetchone()[0]
                conn.commit()
        return url_id

    def get_url_by_id(self, id):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute("SELECT * FROM urls WHERE id = %s", (id,))
                return cursor.fetchone()

    def get_url_by_name(self, name):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute("SELECT * FROM urls WHERE name = %s", (name,))
                return cursor.fetchone()

    def get_all_urls(self):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute("SELECT * FROM urls ORDER BY created_at DESC")
                return cursor.fetchall()

    def add_url_check(self, url_id, status_code, html_values):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO url_checks "
                    "(url_id, status_code, h1, title, description, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (
                        url_id,
                        status_code,
                        html_values.get("h1", ""),
                        html_values.get("title", ""),
                        html_values.get("description", ""),
                        datetime.now()
                    )
                )
                conn.commit()

    def get_checks_for_url(self, url_id):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM url_checks "
                    "WHERE url_id = %s "
                    "ORDER BY created_at DESC",
                    (url_id,)
                )
                return cursor.fetchall()

    def get_last_check_info(self, url_id):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(
                    "SELECT status_code, created_at "
                    "FROM url_checks "
                    "WHERE url_id = %s "
                    "ORDER BY created_at DESC "
                    "LIMIT 1",
                    (url_id,)
                )
                return cursor.fetchone()

    def get_all_last_checks(self):
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute("""
                    SELECT DISTINCT ON (url_id)
                        url_id, status_code, created_at
                    FROM url_checks
                    ORDER BY url_id, created_at DESC
                """)
                rows = cursor.fetchall()
                return {row.url_id: row for row in rows}


url_repo = UrlRepo()
