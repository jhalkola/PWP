# PWP SPRING 2020
# Movie Tracker
# Group information
* Joona Halkola, joona.halkola@gmail.com
* Samuli Peltomaa samulipeltomaa@hotmail.com
* Niklas Vaara niklas.vaara@yahoo.com

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__


## Movie Tracker Database

The database management system is SQLite with version 3.33.0

Requirements.txt has all the needed libraries. To install everything required, run command `python -m pip install .` while in root folder where requirements.txt is located.

Before we can initialize test db and give it some test data we have to set two environment variables. First `set FLASK_APP=movietracker` and next `set FLASK_ENV=development`. These set the flask app name and enable development mode for the testing the API.  
Next, initialize the database by running `flask init-db` after which use `flask testgen` to generate some test data to the db.

Database will have a set of genres, a few movies and series (not all genres have items in them). You can try querying these, here are few example requests to use:  
* [GET] *insert address here where flask is running*/api/genres/ (all the genres)
* [GET] *insert address here where flask is running*/api/genres/action/movies/ (movies in action genre)
* [GET] *insert address here where flask is running*/api/genres/crime/series/ (series in crime genre)

### Database tests

To run the pytest for the database, run command `pytest` in the folder it is located.
