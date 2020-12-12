#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from models import db, Venue, Artist, Show
from forms import *
from flask_wtf import FlaskForm
from logging import Formatter, FileHandler
from flask_migrate import Migrate
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
import babel
import traceback
import dateutil.parser
import json

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@ app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@ app.route('/venues')
def venues():
    # Returns first Venue for each  distinct city/state
    distinct_locations = Venue.query.distinct(Venue.city, Venue.state).all()

    data = []

    for location in distinct_locations:
        d = {"city": location.city, "state": location.state}

        venues_list = Venue.query.filter(
            Venue.city == location.city,
            Venue.state == location.state
        ).all()

        venues = [venue.serialize for venue in venues_list]

        d["venues"] = venues

        data.append(d)

    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')

    search_results = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')
    ).all()

    search_count = len(search_results)

    response = {
        "count": search_count,
        "data": search_results
    }

    return render_template('pages/search_venues.html',
                           results=response,
                           search_term=request.form.get('search_term', '')
                           )


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).one_or_none()

    if venue is None:
        abort(404)

    data = venue.serialize_with_shows

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)

    try:
        new_venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            website=form.website.data,
            image_link=form.image_link.data,
            genres=','.join(form.genres.data),
            facebook_link=form.facebook_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(new_venue)
        db.session.commit()

        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('Error: Venue ' + request.form['name'] + ' could not be added!')
        traceback.print_exc()
    finally:
        db.session.close()

    return render_template('pages/home.html')


@ app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    data = [{"id": a.id, "name": a.name} for a in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term')

    search_results = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')
    ).all()

    search_count = len(search_results)

    response = {
        "count": search_count,
        "data": search_results
    }

    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get('search_term', '')
    )


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)

    if artist is None:
        abort(404)

    data = artist.serialize_with_shows

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id).serialize

    form = ArtistForm(data=artist)

    return render_template(
        'forms/edit_artist.html',
        form=form,
        artist=artist
    )


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)

    try:
        artist = Artist.query.get(artist_id)
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website = form.website.data
        artist.image_link = form.image_link.data
        artist.genres = ','.join(form.genres.data)
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = bool(form.seeking_venue.data)
        artist.seeking_description = form.seeking_description.data

        db.session.commit()

        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('Error: Artist ' +
              request.form['name'] + ' could not be updated!')
        traceback.print_exc()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id).serialize
    form = VenueForm(data=venue)

    return render_template(
        'forms/edit_venue.html',
        form=form,
        venue=venue
    )


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)

    try:
        venue = Venue.query.get(venue_id)
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.website = form.website.data
        venue.image_link = form.image_link.data
        venue.genres = ','.join(form.genres.data)
        venue.facebook_link = form.facebook_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data

        db.session.commit()

        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('Error: Venue ' +
              request.form['name'] + ' could not be updated!')
        traceback.print_exc()
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)

    try:
        new_artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            website=form.website.data,
            image_link=form.image_link.data,
            genres=','.join(form.genres.data),
            facebook_link=form.facebook_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data
        )
        db.session.add(new_artist)
        db.session.commit()

        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('Error: Artist ' + request.form['name'] + ' could not be added!')
        traceback.print_exc()
    finally:
        db.session.close()

    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@ app.route('/shows')
def shows():
    data = [show.serialize for show in Show.query.all()]

    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)

    try:
        new_show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data
        )
        db.session.add(new_show)
        db.session.commit()

        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('Error: Show could not be added!')
        traceback.print_exc()
    finally:
        db.session.close()

    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
