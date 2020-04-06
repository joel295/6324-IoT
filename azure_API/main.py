#!./venv/bin/python3.7

from flask import Flask
from flask_restplus import Resource, Api
from bson import ObjectId
from cosmos_db import get_collection

app = Flask(__name__)
api = Api(app)

# get all documents from specified collection from specified database
# there is one database per customer
# a customers databse can have multiple devices each is its own collection
@api.route('/api/v1/<string:database>/<string:collection>')
class CollectAll(Resource):

    @api.response(200, 'OK')
    @api.response(401, 'AUTHORIZATION FAILED')
    @api.response(404, 'NOT FOUND')
    def get(self, database, collection):
        my_collection = get_collection(database, collection)

        # my_collection is None if authentification failed
        if my_collection == None:
            return {
                "message" : "authentification failed"
            }, 401
        # == [] when my_collection with name collection could not be found in the specified database
        # or database could not be found
        elif [x for x in my_collection.find({})] == []:
            return {
                "message" : "database: {} or collection: {} not found".format(database, collection)
            }, 404
        # remove _id field from document, not json serialisable
        return_list = []
        for document in my_collection.find({}):
            del document['_id']
            return_list.append(document)

        return return_list, 200

# CollectDeviceSensor
@api.route('/api/v1/<string:database>/<string:collection>/<string:field>')
class CollectDeviceSensor(Resource):
    
    @api.response(200, 'OK')
    @api.response(401, 'AUTHORIZATION FAILED')
    @api.response(404, 'NOT FOUND')
    def get(self, database, collection, field):
        my_collection = get_collection(database, collection)

        # my_collection is None if authentification failed
        if my_collection == None:
            return {
                "message" : "authentification failed"
            }, 401
        # == [] when my_collection with name collection could not be found in the specified database
        # or database could not be found
        elif [x for x in my_collection.find({})] == []:
            return {
                "message" : "database: {} or collection: {} not found".format(database, collection)
            }, 404

        # remove _id field from document, not json serialisable
        # remove all sensors except sensor specified by field
        # if field is mispelled, that document will have all sensors removed from data
        # and the header data: epoch and device will exist but data = {}
        return_list = []
        for document in my_collection.find({}):
            curr = {}
            for key in document:
                if key!='_id':
                    curr[key] = document[key]
            data = {}
            for key in document['data']:
                if key==field:
                    data[key] = document['data'][key]
            curr['data'] = data
            return_list.append(curr)

        return return_list, 200


if __name__ == '__main__':
    # run the application
    app.run(debug=True)
