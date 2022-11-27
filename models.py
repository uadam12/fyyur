from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_migrate import Migrate
from flask import abort

db = SQLAlchemy()
moment = Moment()
migrate = Migrate()

def auto_commit(func):
	def committing(*args):
		committed = True
		
		try:
			func(*args)
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			committed = False
			print(e)
		finally:
			db.session.close()
			
		return committed
			
	return committing
		
class Model(db.Model):
	def __init__(self, data={}):
		self.set_data(data)
		
	def set_data(self, data):
		for key, value in data.items():
			if key in ('submit', 'csrf_token') or not value:
				continue
				
			if type(value) == list:
				value = ', '.join(value)
				
			setattr(self, key, value)
	
	@property
	def past_shows(self):
		return [show for show in self.shows_info if show.start_time < datetime.now()]

	@property
	def upcoming_shows(self):
		return [show for show in self.shows_info if show.start_time > datetime.now()]

	@property
	def upcoming_info(self):
		return {
		    "id": self.id,
		    "name": self.name,
		    "num_upcoming_shows": len(self.upcoming_shows)
		}
		
	@classmethod
	def get_recents(cls):
		return [{
            'id': r.id,
            'name': r.name
        } for r in cls.query.order_by(db.desc(cls.created_at)).limit(10).all()]

	@classmethod
	def get(cls, id):
		obj = cls.query.get(id)
		
		if not obj:
			abort(404)
			
		return obj
			
	@classmethod
	@auto_commit
	def create(cls, data):
		obj = cls(data)
		db.session.add(obj)
		
	@classmethod
	@auto_commit
	def delete(cls, id):
		obj = cls.get(id)
		db.session.delete(obj)
		
	@classmethod
	@auto_commit
	def update(cls, id, data):
		obj = cls.get(id)
		obj.set_data(data)

	@classmethod
	def search(cls, term):
		results = cls.query.filter(
            cls.name.ilike(f"%{term}%") |
            cls.state.ilike(f"%{term}%") |
            cls.city.ilike(f"%{term}%") 
        ).all()
		
		return {
            "count": len(results),
            "data": [result.upcoming_info for result in results]
        }
				
	__abstract__ = True
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False)
	city = db.Column(db.String(50), nullable=False)
	state = db.Column(db.String(50), nullable=False)
	phone = db.Column(db.String(20))
	genres = db.Column(db.String(1000), nullable=False)
	image_link = db.Column(db.String(500))
	facebook_link = db.Column(db.String(500))
	website = db.Column(db.String(500))
	seeking_description = db.Column(db.String(1000))
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
	
	def __repr__(self):
		return f'<{self.__class__.__name__} id:{self.id}, name:{self.name}, city:{self.city}, state:{self.state}>'
	

class Venue(Model):
	@classmethod
	def records(cls):
		return [{
            "city": area.city,
            "state": area.state,
            'venues':[
                venue.upcoming_info for venue in cls.query.filter_by(
                    city=area.city, 
                    state=area.state
                ).all()]
        } for area in db.session.query(
		    Venue.state.label("state"), 
		    Venue.city.label("city")
		).distinct(
		    Venue.state, 
		    Venue.city
		).all()]

	__tablename__ = 'venues'

	address = db.Column(db.String(200), nullable=False)
	seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
	shows = db.relationship("Show", backref="venue", lazy=False, cascade="all, delete-orphan")
    
	@property
	def shows_info(self):
		return db.session.query(
    		Artist.id.label('artist_id'),
    		Artist.name.label('artist_name'),
    		Artist.image_link.label('artist_image_link'),
    		Show.start_time.label('start_time')
    	).join(Show).filter(Show.venue_id == self.id).all()
	
	@property
	def details(self):
		return {
          "id": self.id,
          "name": self.name,
          "genres": self.genres.split(", "),
          "city": self.city,
          "state": self.state,
          "phone": self.phone,
		  "address": self.address,
          "website": self.website,
          "facebook_link": self.facebook_link,
          "seeking_description": self.seeking_description,
          "seeking_talent": self.seeking_talent,
          "image_link": self.image_link,
          "past_shows": self.past_shows,
          "upcoming_shows": self.upcoming_shows,
          "past_shows_count": len(self.past_shows),
          "upcoming_shows_count": len(self.upcoming_shows),
        }
		

class Artist(Model):
	@property
	def details(self):
		return {
          "id": self.id,
          "name": self.name,
          "genres": self.genres.split(", "),
          "city": self.city,
          "state": self.state,
          "phone": self.phone,
          "website": self.website,
          "facebook_link": self.facebook_link,
          "seeking_description": self.seeking_description,
          "seeking_venue": self.seeking_venue,
          "image_link": self.image_link,
          "past_shows": self.past_shows,
          "upcoming_shows": self.upcoming_shows,
          "past_shows_count": len(self.past_shows),
          "upcoming_shows_count": len(self.upcoming_shows),
        }
	@property
	def shows_info(self):
		return db.session.query(
			Venue.id.label('venue_id'),
			Venue.name.label('venue_name'),
			Venue.image_link.label('venue_image_link'),
			Show.start_time.label('start_time')
		).join(Show).filter(Show.artist_id == self.id).all()
		
	__tablename__ = 'artists'

	seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
	shows = db.relationship("Show", backref="artist", lazy=False, cascade="all, delete-orphan")
	
	@classmethod
	def records(cls):
		return db.session.query(
			cls.id.label('id'), 
			cls.name.label('name')
		).all()
			
class Show(db.Model):
	def set_data(self, data):
		for key, value in data.items():
			if key in ('submit', 'csrf_token') or not value:
				continue
			elif type(value) == list:
				value = ', '.join(value)
    		
			setattr(self, key, value)

	def __init__(self, data={}):
		self.set_data(data)
    
	@property
	def shows_info(self):
		return db.session.query(
    		Artist.id.label('artist_id'),
    		Artist.name.label('artist_name'),
    		Artist.image_link.label('artist_image_link'),
    		Show.start_time.label('start_time')
    	).join(Show).filter(Show.venue_id == self.id).all()
    		
	@classmethod
	def get(cls, id):
		obj = cls.query.get(id)
		
		if not obj:
			abort(404)
			
		return obj

	@classmethod
	@auto_commit
	def create(cls, data):
		obj = cls(data)
		db.session.add(obj)
    	
	@classmethod
	def records(cls):
		return db.session.query(
    		cls.venue_id.label('venue_id'), 
    		Venue.name.label('venue_name'),
    		cls.artist_id.label('artist_id'), 
    		Artist.name.label('artist_name'),
    		cls.start_time.label('start_time')
    	).join(Venue).join(Artist).all()
			
	__tablename__ = "shows"

	id = db.Column(db.Integer, primary_key=True)
	artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)
	venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
	start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	def __repr__(self):
		return f"<Show id={self.id}, artist_id={self.artist_id}, venue_id={self.venue_id}, start_time={self.start_time}>"