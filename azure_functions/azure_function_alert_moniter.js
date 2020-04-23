module.exports = async function (context, IoTHubMessages) {
    // enables access to mongo db
    var mongoClient = require("mongodb").MongoClient;

    //enables the ability to sentd emails
    var nodemailer = require('nodemailer');
    var transporter = nodemailer.createTransport({
        host: "smtp-mail.outlook.com", // hostname
        secureConnection: false, // TLS requires secureConnection to be false
        port: 587, // port for secure SMTP
        tls: {
            ciphers:'SSLv3'
        },
        auth: {
            user: '',
            pass: ''
        }
    });

    // database and collection for accessing User info 
    var dbName = "Access";
    var collectionName = "Users";

    // connect to User collection in cosmos db
    // connection string to cosmosDB
    url = "mongodb://wastewaterdb:1KE7cHuoAtZ7DkpCWe5Ozr8pSvCicuvF2FJAEtl9TPcNHAdGrnLU5ZY5zyo1Z9WuYjqJLq5aJJuRCWZSya1Vlw%3D%3D@wastewaterdb.mongo.cosmos.azure.com:10255/?ssl=true&appName=@wastewaterdb@"
    const client = await mongoClient.connect(url,{useNewUrlParser: true, authSource: dbName}).catch(err => {context.log(err);});
    if (!client){
        context.log("failed to connect");
        context.done();
    }
    // assuming  IoTHubMessages is a single telemetry message
    // if not, set event hub cardinality fro one to multiple and consider  IoTHubMessages a list of telemetry messages?

    // get all Users because..
    // demo, all users have access to all devices and hub gateways,
    // if real product then filter users on their device and hub access etc
    device    = IoTHubMessages['device'];
    timestamp = IoTHubMessages['time'];
    iotHub    = 'IotGateway1';
    data      = IoTHubMessages['data']; // a dictionary of sensor : value pairs
    senors    = Object.keys(IoTHubMessages['data']); // list of sensor strings found in "data" json dictionary

    var collection = client.db(dbName).collection(collectionName);
    var users = await collection.find({}).toArray(); // all users

    for (var i = 0; i < users.length; i++) {
        curr_username = users[i]['username'];
        email = users[i]['email'];
        alerts = users[i]['alerts']
        for (var j = 0; j < alerts.length; j++) {
            // iterate through alerts, check alerts that match device and iot hub
            // alert_string is of the form "iothub/device/sensor/(warning|danger)/value/(line|above|below)"
            alert_string = Object.keys(alerts[j])[0];
            split = alert_string.split("/");

            // check if alert string is for hub and device AND sensor is in sensors
            if (split[0] == iotHub && split[1] == device && senors.includes(split[2])){
                // check if alert is above or below and if so check if value is above or below indicated value in alert_string
                if (split[5] == 'above' && data[split[2]] > parseFloat(split[4])){
                    // data triggers alert
                    // add timestamp of telemetry message to the alert list in that User's alert that was triggered
                    //NOTE: might want to change to $addToSet to avoid duplicate timestamps
                    var str = `alerts.${j}.${alert_string}`;
                    var query = { username: curr_username};
                    var push = {"$push" : {}};
                    push["$push"][str] = timestamp;

                    //context.log(str);
                    //context.log({query, push});
                    try {
                        response = await collection.update(query, push); 
                        context.log("sent!");
                    } catch (err) {
                        context.log("error!");
                        context.log(err);
                    }
                    
                    if (split[3] == 'danger'){
                        context.log("11111here")
                        // setup e-mail data, even with unicode symbols
                        var mailOptions = {
                            from: '"Waste Water Alert"', // sender address (who sends)
                            to: email, // list of receivers (who receives)
                            subject: 'Danger Alert Trigger', // Subject line
                            text: `Danger alert: ${alert_string} triggered on ${timestamp} with value ${data[split[2]]}` // plaintext body
                        };

                        // send mail with defined transport object
                        try{
                            response = await transporter.sendMail(mailOptions);
                            context.log('email sent');
                        } catch(err){
                            context.log(err);
                            context.log('email failed');
                        }
                    }

                } 
                else if (split[5] == 'below' && data[split[2]] < parseFloat(split[4])){
                   // data triggers alert
                    var str = `alerts.${j}.${alert_string}`;
                    var query = { username: curr_username};
                    var push = {"$push" : {}};
                    push["$push"][str] = timestamp;

                    //context.log(str);
                    //context.log({query, push});
                    try {
                        response = await collection.update(query, push); 
                        context.log("sent!");
                    } catch (err) {
                        context.log("error!");
                        context.log(err);
                    }

                    if (split[3] == 'danger'){
                        context.log("11111here")
                        // setup e-mail data, even with unicode symbols
                        var mailOptions = {
                            from: '"Waste Water Alert"', // sender address (who sends)
                            to: email, // list of receivers (who receives)
                            subject: 'Danger Alert Trigger', // Subject line
                            text: `Danger alert: ${alert_string} triggered on ${timestamp} with value ${data[split[2]]}` // plaintext body
                        };

                        // send mail with defined transport object
                        try{
                            response = await transporter.sendMail(mailOptions);
                            context.log('email sent');
                        } catch(err){
                            context.log(err);
                            context.log('email failed');
                        }
                        
                    }
                } 
            }
            // accessing epoch list in an alert: alerts[j][alert_string]
            //context.log(alert_string);
            //context.log(alerts[j][alert_string]);
        }
    }
    // emails user if a danger alert is triggered else, only alert in web app is raised no email


    //context.log(IoTHubMessages);

    context.done();
};
