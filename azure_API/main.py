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
    @api.response(404, 'NOT FOUND')
    def get(self, database, collection):
        my_collection = get_collection(database, collection)
        if my_collection == None:
            return {
                "message" : "database: {}, collection: {} not found".format(database, collection)
            }, 404

        # remove _id field from document, not json serialisable
        return_list = []
        for document in my_collection.find({}):
            del document['_id']
            return_list.append(document)

        return return_list, 200






if __name__ == '__main__':
    # run the application
    app.run(debug=True)
