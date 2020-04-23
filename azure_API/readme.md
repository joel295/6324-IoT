# Instructions
* On linux to run locally:
    * ensure you have python3.7 installed
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
        ```
    * to run:  
        ```
        $ ./app.py (ensure you chmod +x and set file header as executable)
        or
        $ python3.7 app.py
        ```
* NOTE: disregard main.py it is deprecated now app.py is the main file
