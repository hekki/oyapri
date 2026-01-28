from contextlib import contextmanager
from typing import Generator, cast

import pymysql
from pymysql.connections import Connection
from pymysql.cursors import DictCursor

from app.config import get_settings


@contextmanager
def get_connection(autocommit: bool = True) -> Generator[Connection, None, None]:
    settings = get_settings()
    if not settings.mysql_host or not settings.mysql_user or not settings.mysql_database:
        raise RuntimeError("DB設定が不足しています。")

    ssl_options = None
    if settings.mysql_ca_path:
        ssl_options = {"ca": settings.mysql_ca_path}

    conn = cast(
        Connection,
        pymysql.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=settings.mysql_database,
            autocommit=autocommit,
            cursorclass=DictCursor,
            ssl=ssl_options,
        ),
    )
    try:
        yield conn
    finally:
        conn.close()
