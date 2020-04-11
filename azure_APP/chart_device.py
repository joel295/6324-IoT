
# using a single document entry from the edge device
# return a list of all unique sensors on device
def get_sensors(document):
    sensors = []
    try:
        data = document["data"]
        for key in sorted(data.keys()):
            sensors.append(key)
        return sensors
    except:
        return sensors

# given a document containing device data,
# return the location of that device
def get_location(document):
    try:
        return document["location"]
    except:
        return ""

# given a list of documents of a device and a sensor
# put the time data in the x list and have the corresponding
# sensor data put into the y list
# return both lists as a nested data structure
# x data: get_x_and_y_data(sensor, documents)[0]
# y data: get_x_and_y_data(sensor, documents)[1]
def get_x_and_y_data(sensor, documents):
    x = []
    y = []
    try:
        # for d in documents:
        #     try:
        #         x.append(d["time"])
        #     except:
        #         x.append(0)
        #     try:
        #         y.append(d["data"][sensor])
        #     except:
        #         y.append(0)
        # return [x, y]
        # the below logic adds a dummy y = 0 value when there is no entry
        # found for the 10 seconds before and after an entry, excluding the
        # first entry in the data in the dataset
        for i in range(len(documents)):
            if i > 0 and (documents[i]["time"] - documents[i-1]["time"]) > 10:
                x.append(documents[i]["time"] - 1)
                y.append(0)
            try:
                x.append(documents[i]["time"])
            except:
                x.append(0)
            try:
                y.append(documents[i]["data"][sensor])
            except:
                y.append(0)
            if i < (len(documents) - 1) and (documents[i+1]["time"] - documents[i]["time"]) > 10:
                x.append(documents[i]["time"] + 1)
                y.append(0)
        return [x, y]
    except:
        return [x, y]
