from flask import request, flash, redirect, url_for
from models import db, Venue, Artist, Show

def no_data():
	return not (Venue.query.count() or Artist.query.count())
	
def add_mock_data():
	if not no_data():
		return

	try:
		from mock_data import venues, artists, shows

		for venue in venues:
			Venue.create(venue)
		for artist in artists:
			Artist.create(artist)
		for show in shows:
			Show.create(show)

		flash('Test data are added successfully!!!')
	except:
		flash('Test data are not added')
	
	return {'url': url_for('index')}


# Create models		
def create(cls, form_cls):
    form = form_cls(request.form)
    name = cls.__name__

    if form.validate():
	    if(cls.create(form.data)):
		    flash(f'{name} created successfully!!!')
	    else:
		    flash(f'{name} was not created.')
    else:
	    flash(f'{name} form is invalid')

    return redirect(url_for('index'))
		
# Update models
def update(cls, form_cls, id):
    form = form_cls(request.form)
    name = cls.__name__
	
    if form.validate():
	    if(cls.update(id, form.data)):
		    flash(f'{name} updated successfully!!!')
	    else:
		    flash(f'{name} was not updated.')
    else:
	    flash(f'{name} form is invalid')

    return redirect(url_for('index'))

# Delete models
def delete(cls, id):
	name = cls.__name__

	if(cls.delete(id)):
		flash(f'{name} deleted successfully!!!')
	else:
		flash(f'{name} was not deleted.')
	
	return {'url': url_for('index')}
	
