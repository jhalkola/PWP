# PWP SPRING 2020
# Movie Tracker
# Group information
* Joona Halkola, joona.halkola@gmail.com
* Samuli Peltomaa samulipeltomaa@hotmail.com
* Niklas Vaara niklas.vaara@yahoo.com

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

## Documentation

API documentation can be found from [Apiary](https://movietrackerapi.docs.apiary.io/#).

## Setup Instructions

The database management system is SQLite with version 3.33.0

Requirements.txt has all the needed libraries and Setup.py sets required settings for pytest to run. To install everything required, run command `python -m pip install .` while in folder where requirements.txt and setup.py are located.

Before we can initialize test db and give it some test data we have to set two environment variables. First `set FLASK_APP=movietracker` and next `set FLASK_ENV=development`. These set the flask app name and enable development mode for the testing the API.  
Next, while in root directory of the project, initialize the database by running `flask init-db` after which use `flask testgen` to generate some test data to the db. Lastly, start development server with `flask run`.

If you want to reset the test db, delete "instance" folder which holds the db then run `flask init-db` and `flask testgen` commands again.

### Pytest Instructions

To run the database and API pytests, run command `pytest --disable-pytest-warnings` in the "tests" folder.
