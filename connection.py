import clickhouse_connect
from clickhouse_connect.driver import client, httputil
from contextlib import contextmanager
from django.conf import settings

class DatabaseSessionManager:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = "8123"
        self.username = "admin"
        self.password = "admin"
        self.database = "deltamesh"
        self.client = None

    def connect(self, database):
        if self.client is None:
            self.client = clickhouse_connect.get_client(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                database=database
            )
        return self.client
    
    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    @contextmanager
    def session(self, using="deltamesh"):
        try:
            client = self.connect(database=using)
            yield client
        finally:
            self.close()