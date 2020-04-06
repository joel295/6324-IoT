
from pymongo import MongoClient
import os

URI = "mongodb://wastewater:hF0wcz3mG9aamQ0vP6mlQOIJRVmXapAfLeQ8tS0CtMCNMJqIdVBfhdDcLPSzn0zAxWL2SIrVrTbIinWDXkmDSA==@wastewater.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@wastewater@"
name = "wastewater"
password = "hF0wcz3mG9aamQ0vP6mlQOIJRVmXapAfLeQ8tS0CtMCNMJqIdVBfhdDcLPSzn0zAxWL2SIrVrTbIinWDXkmDSA=="

# provided database name and collection (both strings) return collection
# database and collection need to be valid resource names from azure cosmos db
def get_collection(database, collection):
    try:
        # use for local testing
        client = MongoClient(URI)
        db = client[database] # select the database
        db.authenticate(name=name, password=password)

        # use for deployed use and fill credentials
        # client = MongoClient(os.getenv("MONGOURL"))
        # db = client.test
        #db.authenticate(name=os.getenv("MONGO_USERNAME"),password=os.getenv("MONGO_PASSWORD"))

        my_collection = db[collection]
        return my_collection
    except:
        return None
