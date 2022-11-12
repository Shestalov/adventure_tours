# import random
# import uuid

from pymongo import MongoClient


class MongoDBConnection:

    def __init__(self, username, password, hostname, port):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port

        self.client = None

    def __enter__(self):
        CONNECTION_STRING = f"mongodb://{self.username}:{self.password}@{self.hostname}:{self.port}"
        self.client = MongoClient(CONNECTION_STRING)
        self.db = self.client['test']
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

# if __name__ == '__main__':

# with MongoDBConnection('admin', 'admin', '127.0.0.1') as db:

# for adding random stopping in stopping collections
# collection = db['stopping']
# collection.insert_one({'points': [{'name': f'point_{uuid.uuid4}', 'lat': random.random(),
#                                    'lon': random.random()},
#                                   {'name': f'point_{uuid.uuid4}', 'lat': random.random(),
#                                    'lon': random.random()}]})

# for adding users in event_users
# collection = db['event_users']
# collection.insert_one({"pending": [1, 2, 3], "accepted": [4, 5]})
# print(collection.find_one())
