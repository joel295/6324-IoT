#!./venv/bin/python3.7

from client_util import *
import random
import time

if __name__ == '__main__':
    # dummy data
    try:
        client = init_client_device()
        print("IOT hub activated, press Ctrl-C to exit")
        print("This Device: " + get_device())
        print("Host: " + get_host())

        while True:
            # device represents edge device recieving data from
            device = "edge_device1"
            location = "location1"
            epoch = int(time.time())
            data = {
                "temperature" : 20 + (random.random() * 15),
                "turbidity" : (random.random() * 30),
                "tds" : (random.random() * 60)
            }

            message = create_message(device, location, epoch, data)
            status = send_message(client, message)
            if status == 1: # failed to send
                # try to send until status is successful: status = 0
                while not status:
                    status = send_message(client, message)
                    time.sleep(1)
            time.sleep(5)

    except KeyboardInterrupt:
        print(get_device() + " Stopped client")
