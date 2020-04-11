
from pymongo import MongoClient
import os

URI = "mongodb://wastewaterdb:1KE7cHuoAtZ7DkpCWe5Ozr8pSvCicuvF2FJAEtl9TPcNHAdGrnLU5ZY5zyo1Z9WuYjqJLq5aJJuRCWZSya1Vlw==@wastewaterdb.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@wastewaterdb@"
name = "wastewaterdb"
password = "1KE7cHuoAtZ7DkpCWe5Ozr8pSvCicuvF2FJAEtl9TPcNHAdGrnLU5ZY5zyo1Z9WuYjqJLq5aJJuRCWZSya1Vlw=="

# provided database name and collection (both strings) return collection
# database and collection need to be valid resource names from azure cosmos db
def get_collection(database, collection):
    try:
        client = MongoClient(URI)
        db = client[database] # select the database
        db.authenticate(name=name, password=password)

        my_collection = db[collection]

        return [x for x in my_collection.find({})]
    except:
        return [] # failed to authenticate

# given a valid database name, a list of collections in that database is returned
#
def query_for_collections(database):
    try:
        client = MongoClient(URI)
        db = client[database] # select the database
        db.authenticate(name=name, password=password)

        return db.list_collection_names()
    except:
        return [] # failed to authenticate

# add get devices from a gateway
