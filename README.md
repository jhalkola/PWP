# PWP SPRING 2020
# Movie Tracker
# Group information
* Joona Halkola, joona.halkola@gmail.com
* Samuli Peltomaa samulipeltomaa@hotmail.com
* Niklas Vaara niklas.vaara@yahoo.com

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

## Documentation

API documentation can be found from [Apiary](https://movietrackerapi.docs.apiary.io/#).

## Dependencies

Jquery external library file can found in movietracker/static/scripts/ which includes all needed information about the library.
All other libraries and their versions can be found from requirement.txt.

## Setup Instructions

Requirements.txt has all the needed libraries and Setup.py sets required settings for pytest to run. To install everything required, run command `python -m pip install .` while in folder where requirements.txt and setup.py are located.

The database management system is SQLite with version 3.33.0

Step for initializing database and adding test data, run these commands in root directory:  
1. `set FLASK_APP=movietracker` (set flask app name)  
2. `set FLASK_ENV=development` (set flask to run in development mode)  
3. `flask init-db` (initialize database)  
4. `flask testgen` (generate test data)  

If you want to reset the test db, delete "instance" folder and run above commands again.

## Flask Test Server
 
To start development server, use `flask run`. Environmental variables FLASK_APP and FLASK_ENV must be set.

## Pytests

To run the database and API pytests, run command `pytest --disable-pytest-warnings` in the "tests" folder.  
To run pytest with coverage, use `pytest --disable-pytest-warnings --cov-report term-missing --cov=movietracker`.  
--disable-pytest-warnings is used to make the test output a bit cleaner, as pytest wants to show bunch of deprecation warnings which have nothing to do with our tests.

## Client

To test the client, do as setup instructions says, after which you can start the flask server with `flask run`. You can access the client from web browser (only Firefox and Chrome tested to work) via `http://127.0.0.1:5000/` and start to explore the client.
