
import json

def get_number_of_documents(documents):
    return len(documents)

def get_unique_devices(documents):
    devices = []
    for d in documents:
        devices.append(d['device'])
    return list(set(devices))

def get_device_info(documents):
    devices = []
    for d in documents:
        info = {
            "device" : d['device'],
            "location" : d['location'],
            "sensors" : sorted(d['data'].keys()) # get sensor keys and sort them alphabetically
        }
        devices.append(json.dumps(info))
    unique_devices = list(set(devices))
    info = []
    for u_d in unique_devices:
        info.append(json.loads(u_d))
    return info
