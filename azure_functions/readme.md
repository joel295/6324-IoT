# Instructions
This folder contains javascript functions that run in Azure function apps.  
Their purpose is to transfer data from iot hub to Cosmos DB within cloud platform.  
The azure function is triggered when gateway device sends telemetry to IoT hub.  
Only need one azure function to send telemetry from iot hub to CosmosDB.  
Can change code in azure function to switch endpoint DB collection telemetry is sent to depending on edge gateway etc.  
