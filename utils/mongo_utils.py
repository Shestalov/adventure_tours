from pymongo import MongoClient

client = MongoClient('localhost', 27017)


class MongoDBConnection:

    def __init__(self, username, password, hostname, port=27017):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client = None

    def __enter__(self):
        CONNECTION_STRING = f"mongo+srv://{self.username}:{self.password}@{self.hostname}:{self.port}"
        self.client = MongoClient(CONNECTION_STRING)
        # self.db = self.client['test']
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
