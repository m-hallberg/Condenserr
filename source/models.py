from datetime import datetime, timezone

from . import db

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.now())
    tmdb_id = db.Column(db.String(100))
    tvdb_id = db.Column(db.String(100))
    img_url = db.Column(db.String(100))
    local_url = db.Column(db.String(100))

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    series_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    series = db.relationship(
        'Item',
        backref=db.backref('episodes', lazy=True)
    )
    tvdb_id = db.Column(db.String(100))
    tmdb_id = db.Column(db.String(100))
    imdb_id = db.Column(db.String(100))
    img_url = db.Column(db.String(100))
    season = db.Column(db.Integer)
    episode = db.Column(db.Integer)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    event = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone.utc))