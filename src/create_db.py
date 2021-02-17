from app import db, Movie, Series, Genre

db.create_all()
db.session.add(Genre(name="Action"))
db.session.add(Genre(name="Crime"))
db.session.commit()

db.session.add(Movie(
        title="The Avengers",
        actors="Robert Downey Jr.",
        release_date="11-04-2012",
        score=8.0,
        genre=Genre.query.filter_by(name="Action").first()
))

db.session.add(Series(
        title = "Breaking Bad",
        actors = "Bryan Cranston",
        release_date = "20-01-2008",
        score = 9.5,
        seasons = 5,
        genre=Genre.query.filter_by(name="Crime").first()
))
db.session.commit()