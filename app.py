#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask import Flask, render_template, request
import logging
from logging import Formatter, FileHandler
#from flask_wtf import Form
from forms import *
from models import moment, db, migrate, Venue, Artist, Show
from datetime import datetime
from crud import no_data, create, update, delete, add_mock_data

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment.init_app(app)
app.config.from_object('config')
app.app_context().push()
db.init_app(app)
migrate.init_app(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def format_datetime(date, format='medium'):
    if type(date) == str:
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")

    if format == 'full':
        format = "%A %B, %d, %Y at %H:%M%p"
    elif format == 'medium':
        format = "%a %b, %d, %Y %H:%M%p"

    return date.strftime(format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return add_mock_data()

    return render_template(
        'pages/home.html', 
        venues=Venue.get_recents(), 
        artists=Artist.get_recents(),
        no_data = no_data()
    )


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues/')
def venues():
    return render_template(
        'pages/venues.html', 
        areas=Venue.records()
    )


@app.route('/venues/<int:venue_id>/', methods=['GET', 'DELETE'])
def show_venue(venue_id):
    if request.method == 'DELETE':
        return delete(Venue, venue_id)

    venue = Venue.get(venue_id)

    return render_template(
        'pages/show_venue.html', 
        venue=venue.details
    )


#  ----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['POST', 'GET'])
def create_venue():
    if request.method == 'POST':
        return create(Venue, VenueForm)

    return render_template('forms/new_venue.html', form=VenueForm())

#  Update Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET', 'POST'])
def edit_venue(venue_id):
    if request.method == "POST":
        return update(Venue, VenueForm, venue_id)

    form = VenueForm()
    venue = Venue.get(venue_id)
    form.genres.data = venue.genres.split(", ")
    
    return render_template('forms/edit_venue.html', form=form, venue=venue)

#  Search Venue
#  ----------------------------------------------------------------

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get("search_term", "")

    return render_template(
        'pages/search_venues.html', 
        results=Venue.search(search_term), 
        search_term=search_term
    )

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists/')
def artists():
    return render_template(
        'pages/artists.html', 
        artists=Artist.records()
    )


@app.route('/artists/<int:artist_id>/', methods=['GET', 'DELETE'])
def show_artist(artist_id):
    if request.method == 'DELETE':
        return delete(Artist, artist_id)

    artist = Artist.get(artist_id)

    return render_template(
        'pages/show_artist.html', 
        artist=artist.details
    )


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['POST', 'GET'])
def create_artist():
    if request.method == 'POST':
        return create(Artist, ArtistForm)

    return render_template('forms/new_artist.html', form=ArtistForm())

#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['POST', 'GET'])
def edit_artist(artist_id):
    if request.method == "POST":
        return update(Artist, ArtistForm, artist_id)

    artist = Artist.get(artist_id)
    form = ArtistForm()
    form.genres.data = artist.genres.split(", ")

    return render_template('forms/edit_artist.html', form=form, artist=artist)

#  Delete Artist
#  ----------------------------------------------------------------

#  Search Artist
#  ----------------------------------------------------------------

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get("search_term", "")

    return render_template(
        'pages/search_artists.html', 
        results=Artist.search(search_term), 
        search_term=search_term
    )


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows/')
def shows():
    return render_template(
        'pages/shows.html', 
        shows= Show.records()
    )




@app.route('/shows/create', methods=['GET', 'POST'])
def create_shows():
    if request.method == 'POST':
        return create(Show, ShowForm)
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
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
#if __name__ == '__main__':
#    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
