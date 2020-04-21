
from pymongo import MongoClient
import datetime

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

def get_device_documents(database, collection, device_name):
    try:
        client = MongoClient(URI)
        db = client[database] # select the database
        db.authenticate(name=name, password=password)

        my_collection = db[collection]

        # return a list of documents where "device" = device_name
        return [x for x in my_collection.find({"device" : device_name})]
    except:
        return [] # failed to authenticate

# return a document (represents a registered user) from the Access -> Users collection
# the document  must match the query made from the dictionary query which has form {'attr':value}
# returns only one user, for security reasons
def query_user_data(query):
    if query == {}:
        return None
    try:
        client = MongoClient(URI)
        db = client["Access"] # select the database
        db.authenticate(name=name, password=password)

        my_collection = db["Users"]
        users = [x for x in my_collection.find(query)]
        return users[0] # a user is a dictionary following the document User schema
    except:
        return None # failed to authenticate or no users found

# writes a new user to the Access -> Users collection
# details is a python dictionary following the format below
# details = {
#     "username" : username,
#     "email"    : email,
#     "password" : password
# }
# note _id is added to the document once written to db by default
# _id is used as id in the Users class
# function returns false if failure to write user, true otherwise
def write_new_user(details):
    try:
        client = MongoClient(URI)
        db = client["Access"] # select the database
        db.authenticate(name=name, password=password)

        my_collection = db["Users"]

        # check if a user with the same username exists in the database:
        query = {"username" : details["username"]}
        if query_user_data(query) != None: # note None could also be the result of a failed authenticate
            return False

        # insert user since username is unique
        _id = my_collection.insert_one(details).inserted_id
        if _id:
            return True
    except:
        return False # failed to authenticate
# alerts is a list of path strings of the form: hub/device/sensor/(warning|danger)/value/(above/below/line)
# each path string is a key to a list of epoch times for which the alert was triggered
# alerts = [
#     "pathString" : [
#         time1,
#         time2
#     ]
# ]
# given user id, hub and device get the user alerts of the form:
# hub/device/
def get_relevent_alert_path_strings(username, hub, device, sensors):
    # get current user document given username
    query = {"username" : username}
    user = query_user_data(query)
    if user == None:
        return {}
    # retrieve alerts
    alerts = user['alerts']

    # filter alerts and get those which have hub and device
    # add only [sensor, (warning|danger), value, (+|-)] path string to the final_list, values are not neaded
    final_alerts = {}
    # initialise final_alerts
    for s in sensors:
        final_alerts[s] = {}
        final_alerts[s]['warning'] = {'value' : 0, 'trigger' : 'line'}
        final_alerts[s]['danger'] =  {'value' : 0, 'trigger' : 'line'}
    #print(final_alerts)
        # overwrite final_alerts with db alert data
    for a in alerts:
        alert_string = ""
        for key in a.keys():
            alert_string = key
        a_split = alert_string.split('/')
        # a is the path string of the form: "hub/device/sensor/(warning|danger)/value/(above/below/line)"
        # print(a_split[2] + " " + a_split[3] + " " + a_split[4] + " " + a_split[5] )
        # print(hub + " " + device)
        # print(a_split[0] + " " + a_split[1])
        if a_split[0] == hub and a_split[1] == device:
            final_alerts[a_split[2]][a_split[3]] = {
                "value"  : int(a_split[4]),
                "trigger": a_split[5]
            }
    #print(final_alerts)
    return final_alerts



def write_alert_to_db(username, new_alert):
    query = {"username" : username}
    user = query_user_data(query)

    if user == None:
        return None # failed to get user
    # retrieve alerts
    alerts = user['alerts']
    do_not_write_flag = False
    if alerts:
        nabp = new_alert.split('/')
        new_alert_base_path = nabp[0] + '/' + nabp[1] + '/' + nabp[2] + '/' + nabp[3] + '/'
        old_alert_string = ""
        epoch_list = []
        for a in alerts:
            # find the alert in the db that the new_alert will replace
            # old_alert and new_alert with the same string up to "hub/device/sensor/(warning|danger)/"
            # refer to the same alert, therefore replace alert with new_alert
            alert_string = ""
            for key in a.keys():
                alert_string = key

            # check if new_alert and alert_string (current alert string) are the same, if so don't write to db
            if new_alert == alert_string:
                do_not_write_flag = True
                break

            oabp = alert_string.split('/')
            old_alert_base_path = oabp[0] + '/' + oabp[1] + '/' + oabp[2] + '/' + oabp[3] + '/'
            if new_alert_base_path == old_alert_base_path:
                old_alert_string = alert_string
                epoch_list = a[old_alert_string]
                break
                # after finding a (alert string to replace), remove it from alert list, recall flag holds a
        # remove old alert  and its epoch list from alerts
        if {old_alert_string : epoch_list} in alerts and not do_not_write_flag:
            alerts.remove({old_alert_string : epoch_list})
        # add new replacement alert to alerts but keep the old alerts epoch list
        alerts.append({new_alert : epoch_list})
    else:
        # if no old alert that matches this alert add it as a new alert with epock list empty: []
        alerts.append({new_alert : []})
    #try:
    if not do_not_write_flag:
        client = MongoClient(URI)
        db = client["Access"] # select the database
        db.authenticate(name=name, password=password)

        my_collection = db["Users"]
        x = my_collection.update(query, {"$set" : {"alerts": alerts} })
        if not x:
            return None
    # except:
    #     return None # failed to authenticate or no users found
    return True

# get alert data from database for a user with username = username
# return a formated list of the data of the alert plus the list of triggered epoch times
def get_alert_data(username):
    query = {"username" : username}
    user = query_user_data(query)

    if user == None:
        return [[], 0] # failed to get user
    # retrieve alerts
    alerts = user['alerts']
    alert_data = [] # final result to be returned by this function
    alert_number = 0 # for the dashboard Alerts icon, a sum of all alerts that have been triggered across all user alerts
    for alert in alerts:
        # get alert string from the alert dictionary entry of the form: {alert_string : [list of epochs]}
        alert_string = ""
        for key in alert.keys(): # an alert only has one alert_string so this only loops once
            alert_string = key
        alert_string_data = alert_string.split('/')

        # convert epoch times to local time
        # if UTC is desired: datetime.datetime.utcfromtimestamp(int(epoch)).strftime('%Y-%m-%d %H:%M:%S')
        epoch_list = alert[alert_string]
        timestamp_list = []
        alert_number += len(epoch_list) # adds number of times the current alert has been triggered
        for epoch in epoch_list:
            timestamp_list.append(datetime.datetime.fromtimestamp(int(epoch)).strftime('%Y-%m-%d %H:%M:%S'))
        alert_data.append([alert_string_data[0], alert_string_data[1], alert_string_data[2], alert_string_data[3], alert_string_data[4], alert_string_data[5], timestamp_list])
    return [alert_data, alert_number]
