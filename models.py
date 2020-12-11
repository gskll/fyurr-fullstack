from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import datetime
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(120))

    def __repr__(self):
        return f'<Venue#{self.id}: {self.name}>'

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'address': self.address,
                'phone': self.phone,
                'website': self.website,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'genres': self.genres.split(','),
                'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description,
                }

    @property
    def serialize_all_shows(self):
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'address': self.address,
                'phone': self.phone,
                'website': self.website,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'genres': self.genres.split(','),
                'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description,
                'num_upcoming_shows': Show.query.filter(
                    Show.start_time > datetime.datetime.now(),
                    Show.venue_id == self.id)
                }


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(120))

    def __repr__(self):
        return f'<Artist#{self.id}: {self.name}>'

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'website': self.website,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'genres': self.genres.split(','),
                'seeking_venue': self.seeking_venue,
                'seeking_description': self.seeking_description,
                }


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(), nullable=False)

    # foreign keys
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)

    # relationships
    artist = db.relationship(
        'Artist', backref=db.backref('shows', cascade='all, delete'))
    venue = db.relationship('Venue', backref=db.backref(
        'shows', cascade='all,delete'))

    def __repr__(self):
        return f'<Show#{self.id}: {self.artist} {self.venue}>'
