# Instructions
* On linux to run locally:
    * Have python3.7 installed
    * in program directory: setup virtualenv
    * depending on where your python3.7 is:
    ```
        $ virtualenv -p /usr/local/bin/python3.7 ./venv
        or 
        $ virtualenv -p /usr/bin/python3.7 ./venv
        or 
        $ virtualenv ./venv
    ```
    * then to activate:
    ```
        $ source venv/bin/activate
        $ pip3.7 install -r requirements.txt
        to run:
        $ ./main.py
        or 
        $ python3 main.py
    ```