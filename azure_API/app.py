
from flask import Flask
from flask_restplus import Resource, Api
from bson import ObjectId
from cosmos_db import get_collection, query_for_collections

app = Flask(__name__)
api = Api(app)

# Get the names of the available collections in the specified database.
@api.route('/api/v1/<string:database>/')
class QueryCollections(Resource):

    @api.response(200, 'OK')
    @api.response(401, 'AUTHORIZATION FAILED')
    @api.response(404, 'NOT FOUND')
    @api.param('database', 'Database')
    @api.doc(description="Get the names of the available collections in the specified database.")
    def get(self, database):
        query = query_for_collections(database)

        if query == None:
            return {
                "message" : "authentification failed"
            }, 401
        if query == []:
            return {
                "message" : "database: {} not found or no collections".format(database)
            }, 404

        return_data = {
            "collections" : query
        }
        return return_data, 200

# Get all documents from specified collection from specified database.
# There is one database per customer.
# A customers database can have multiple devices each is its own collection.
@api.route('/api/v1/<string:database>/<string:collection>')
class CollectAll(Resource):

    @api.response(200, 'OK')
    @api.response(401, 'AUTHORIZATION FAILED')
    @api.response(404, 'NOT FOUND')
    @api.param('database', 'Database')
    @api.param('collection', 'Collection')
    @api.doc(description="Get all documents from specified collection from specified database.")
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
    @api.param('database', 'Database')
    @api.param('collection', 'Collection')
    @api.param('field', 'Field')
    @api.doc(description="Get a particular document from specified collection from specified database.")
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

        # remove _id field from document, not JSON serialisable
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
