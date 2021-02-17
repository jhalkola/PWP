# PWP SPRING 2020
# Movie Tracker
# Group information
* Joona Halkola, joona.halkola@gmail.com
* Samuli Peltomaa samulipeltomaa@hotmail.com
* Niklas Vaara niklas.vaara@yahoo.com

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__


## Movie Tracker Database

The database management system is SQLite with version 3.33.0

Requirements.txt has all the needed libraries. To install, run command `python -m pip install -r requirements.txt`.

To setup the database, run command `python create_db.py`. This creates the database framework and populates it with two genres, action and comedy, and creates one movie and one series. The movie is linked to "Action" genre and series is linked to "Crime" genre.
