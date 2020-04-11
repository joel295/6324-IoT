
from flask import Flask, render_template
from cosmos_db import get_collection, query_for_collections
from dashboard import get_number_of_documents, get_unique_devices, get_device_info

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

# finds the metadata of hubs, devices, and their sensors
# displays data on the dashboard
@app.route('/dashboard')
def dashboard():
    device_data = []
    gateway_data = []
    tm_dashboard = 0
    ud_dashboard = 0
    us_dashboard = []
    database = "Messages"
    collections = query_for_collections(database)

    for collection in collections:
        documents = get_collection(database, collection)
        g_data = []
        g_data.append(collection)

        # get unique devices and add them to count for dashboard metrics
        ud = get_unique_devices(documents)
        ud_dashboard += len(ud)
        g_data.append("   ".join(ud))

        # get total telemetry messages and add them to count for dashboard metrics
        tm = get_number_of_documents(documents)
        tm_dashboard += tm
        g_data.append(tm)

        g_data.append("NA")
        gateway_data.append(g_data)
        info = get_device_info(documents)
        for i in info:
            d_data = []
            d_data.append(i["device"])
            d_data.append("   ".join(i["sensors"]))
            d_data.append(i["location"])
            d_data.append(collection)
            device_data.append(d_data)
            for s in i["sensors"]:
                us_dashboard.append(s)
        us_dashboard = len(list(set(us_dashboard)))
        dashboard_data = [tm_dashboard, ud_dashboard, us_dashboard, 0]
    return render_template("dashboard.html", device_data = device_data, gateway_data = gateway_data, dashboard_data = dashboard_data)

if __name__ == '__main__':
    # run the application
    app.run(debug=True)
