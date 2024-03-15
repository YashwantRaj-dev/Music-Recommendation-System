# Define your models

from config import db
from datetime import datetime

class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        name = db.Column(db.String(64), nullable = True)
        password = db.Column(db.String(120), nullable=False)

        def __repr__(self):
                return '<User %r>' % self.username

        @classmethod
        def return_users(cls):
                return cls.query.all()

        @classmethod
        def create_user(cls, username, password):
                new_user = cls(username=username, password=password)
                db.session.add(new_user)
                db.session.commit()
                return new_user

        @classmethod
        def get_user_by_uname(cls, uname):
                return cls.query.filter_by(username=uname).first()




class Album(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        album_name = db.Column(db.String(100), nullable=False)
    
    # Define one-to-many relationship with Song
        songs = db.relationship('Song', backref='album', lazy=True, cascade='all, delete-orphan')

        creator_id = db.Column(db.Integer, db.ForeignKey('creator.id'), nullable=False)
        creator = db.relationship('Creator', back_populates='albums')

        def __repr__(self):
                return f'<Album {self.album_name} by {self.creator.username}>'

class Song(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        singer_name = db.Column(db.String(64), nullable=True) 
        release_date = db.Column(db.Date, nullable=True)
        lyrics = db.Column(db.Text, nullable=True)
        rating = db.Column(db.Float, nullable=True)
        genre = db.Column(db.String(100), nullable=False) 
    # Define many-to-one relationship with Album
        album_id = db.Column(db.Integer, db.ForeignKey('album.id', ondelete='CASCADE'), nullable=False)
        #album = db.relationship('Album',backref=db.backref('songs', lazy=True)) 
        
        creator_id = db.Column(db.Integer, db.ForeignKey('creator.id'), nullable=False)
        #creator = db.relationship('Creator', back_populates='songs') 

        def __repr__(self):
                return f'<Song {self.name} by {self.creator.username}>'

class Creator(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True, nullable=False)
        password = db.Column(db.String(120), nullable=False)
        songs = db.relationship('Song', backref='creator', lazy=True,cascade='all, delete-orphan')
        albums = db.relationship('Album', back_populates='creator', lazy=True,cascade='all, delete-orphan')
        number_of_albums = db.Column(db.Integer, default=0)

        def __repr__(self):
                return '<Creator %r>' % self.username
    
        @classmethod
        def create_creator(cls, username, password, number_of_albums):
                new_creator = cls(username=username, password=password, number_of_albums=number_of_albums)
                db.session.add(new_creator)
                db.session.commit()
                return new_creator 
        
        @classmethod
        def create_song(cls,creator, title, singer, album_name, release_date, lyrics,genre): 
        
                album = Album.query.filter_by(album_name=album_name, creator_id=creator.id).first()
                if not album:
                        album = Album(album_name=album_name, creator=creator)
                        db.session.add(album)

                        creator.number_of_albums += 1
                        db.session.commit()

                #try:
            # Try to convert release_date string to Python date object
                release_date = datetime.strptime(release_date, '%Y-%m-%d').date()
                #except ValueError:
                #        return "Invalid date format. Please use the format 'DD-MM-YYYY'."

                # Create a new song
                new_song = Song(name=title, singer_name=singer, release_date=release_date, lyrics=lyrics, creator=creator, album=album,genre=genre,rating=0)
                db.session.add(new_song)
                db.session.commit()

                return new_song 
        
        
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<Admin {self.username}>'


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    
    songs = db.relationship('Song', secondary='playlist_songs', backref=db.backref('playlists', lazy=True))

class PlaylistSongs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)