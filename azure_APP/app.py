
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

from cosmos_db import get_collection, query_for_collections, get_device_documents, query_user_data, write_new_user, get_relevent_alert_path_strings, write_alert_to_db, get_alert_data
from dashboard import get_number_of_documents, get_unique_devices, get_device_info
from chart_device import get_sensors, get_location, get_x_and_y_data
from bson.objectid import ObjectId

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

# given id find user
# must return None if ID is not accepted
@login_manager.user_loader
def load_user(user_id):
    #find user with username in db
    # initialize a User object from the data from
    query = {"_id" : ObjectId(user_id)}
    user = query_user_data(query)
    if user == None:
        print("loading user: failed returning None")
        return None
    return User(str(user['_id']), user['username'], user['email'], user['password'])

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # go to https://stackoverflow.com/questions/54992412/flask-login-usermixin-class-with-a-mongodb
        # get user from database given Username
        # initialise class using details from ser
        # username: form.username.data
        query = {"username" : form.username.data}
        potential_user = query_user_data(query)
        if potential_user != None:
            user = User(str(potential_user['_id']), potential_user['username'], potential_user['email'], potential_user['password'])
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = {
            "username" : form.username.data,
            "email"    : form.email.data,
            "password" : hashed_password,
            "alerts" : [] # maintains the user defined sensor alerts
        }
        #NOTE check if fails when two users exist with the same username
        #NOTE if the fail does not occur, check if the username exists and or email within databse before adding new user
        status = write_new_user(new_user)
        if status:
            return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# finds the metadata of hubs, devices, and their sensors
# displays data on the dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    device_data = []
    gateway_data = []
    tm_dashboard = 0
    ud_dashboard = 0
    us_dashboard = []
    al_dashboard = 0 # count of total triggered alerts
    database = "Messages"
    collections = query_for_collections(database)
    alert_data_list = get_alert_data(current_user.username) # alert data of form [alert_data, sum_of_triggered_alerts]
    alert_data = alert_data_list[0]
    al_dashboard = alert_data_list[1]

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
        dashboard_data = [tm_dashboard, ud_dashboard, us_dashboard, al_dashboard] # last entry is for alerts, to be implemented later
    return render_template("dashboard.html", device_data = device_data, gateway_data = gateway_data, dashboard_data = dashboard_data, alert_data=alert_data, username = current_user.username)

@app.route('/chart_device/<gateway>/<device>', methods=["GET", "POST"])
@login_required
def chart_device(gateway, device):
    documents = get_device_documents("Messages", gateway, device)
    # sort documents based on ascending epoch time before chart preparation
    # ensures documents are in order even though the data is time series
    documents = sorted(documents, key=lambda x: x["time"], reverse=False)

    location = get_location(documents[0])
    sensors = get_sensors(documents[0])
    data = {}
    for s in sensors:
        graph_data = get_x_and_y_data(s, documents)
        data[s] = {
            "x_axis" : graph_data[0], # time
            "y_axis" : graph_data[1]  # values
        }

    # thresholds is a dictionary containing two horizontal lines for epa and custom thresholds for each sensor
    # the user if they request a threshold at y=5, they type in 5 in the corresponding threshold box for the
    # corresponding sensor
    # below catpures that input else the default is 0,
    # chartjs-plugin-annotation is a plugin used to create these graph lines and can be seen in chart_device.html
    # under the annotations in options in the script
    thresholds = {}

    # get alert thresholds and put them into the threshold structure
    thresholds = get_relevent_alert_path_strings(current_user.username, gateway, device, sensors)
    # remove a sensor from alerts if theywhere removed from device after last POST
    for key in thresholds:
        if not key in sensors:
            del thresholds[key]

    if request.method == "POST":
        for s in sensors:
            #add POSTed data to thresholds, so users can view it in template
            try:
                value = request.form["warning_value_" + s]
                trigger = request.form["warning_trigger_" + s]
                # if value and trigger exist, overwrite alert thresholds with the POSTed values
                if value and trigger:
                    thresholds[s]['warning'] = {
                        "value" : value,
                        "trigger" : trigger
                    }
                # write new POST alert string into datbase
                # string in database has the following structure:
                # "hub/device/sensor/(warning|danger)/value/(above/below/line)"
                # only write alert if not default '0/line'
                if not '/' + trigger == '/line':
                    alert_string = gateway + '/' + device + '/' + s + '/' + 'warning' + '/' + str(value) + '/' + trigger
                    if not write_alert_to_db(current_user.username, alert_string):
                        print("FAILED TO WRITE ALERT")
            except:
                pass # the dictionary with no meaningful data initialised in get_relevent_alert_path_strings
            try:
                value = request.form["danger_value_" + s]
                trigger = request.form["danger_trigger_" + s]
                # if value and trigger exist, overwrite alert thresholds with the POSTed values
                if value and trigger:
                    thresholds[s]['danger'] = {
                        "value" : value,
                        "trigger" : trigger
                    }
                if not '/' + trigger == '/line':
                    alert_string = gateway + '/' + device + '/' + s + '/' + 'danger' + '/' + str(value) + '/' + trigger
                    if not write_alert_to_db(current_user.username, alert_string):
                        print("FAILED TO WRITE ALERT")
            except:
                pass # the dictionary with no meaningful data initialised in get_relevent_alert_path_strings

    return render_template("chart_device.html", device=device, gateway=gateway, sensors=" ".join(sensors), location=location, thresholds=thresholds, data=data, username = current_user.username)

if __name__ == '__main__':
    # run the application
    app.run(debug=True)
