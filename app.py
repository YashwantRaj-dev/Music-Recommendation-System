from flask import render_template, request, redirect, url_for, session, flash 

from config import app, db
from models.user import User, Album, Song, Creator, Playlist, PlaylistSongs
import search
from sqlalchemy import func
from datetime import datetime
from sqlalchemy import or_

@app.route('/')
def index_template():
    return render_template('index.html')

@app.route('/login')
def login_template():
    return render_template('login.html')

@app.route('/register')
def register_template():
    return render_template('register.html')

@app.route('/user-home', methods=['GET', 'POST'])
def login_validation():
    if request.method == 'POST':
        uname = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.get_user_by_uname(uname)

        session['username'] = uname
        #existing_creator = Creator.get_creator_by_uname(uname)
        creator_account_exists = Creator.query.filter_by(username=uname).first() is not None

        genres = db.session.query(Song.genre.distinct()).all()
        genres_and_songs = []
        for genre in genres:
            genre_name = genre[0] 
            # Fetch songs for each genre
            songs = Song.query.filter_by(genre=genre_name).all()
            genres_and_songs.append({'genre': genre_name, 'songs': songs})
        
        if existing_user and existing_user.password == password:
            return render_template('userhomepage.html', username=uname, creator_account_exists=creator_account_exists,genres_and_songs=genres_and_songs)
        else:
            return "<h1>Invalid Credentials</h1>"
        
    else:
        
        return render_template('login.html')


@app.route('/register-validation', methods=['POST'])
def register_validation():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        User.create_user(username, password)
        return {
            "status": "success",
            "message": f"User created successfully {username}"
        }
    except Exception as e:
        return "There was an error creating the user: {}".format(e) 


@app.route('/search', methods=['GET'])
def search_songs():
    query = request.args.get('search_query')
    search_results = search.search_songs(query)  # Use the search function from your search.py module
    return render_template('userhomepage.html', search_results=search_results)


@app.route('/creator-registration')
def creator_registration():
    return render_template('creatorregistration.html')

@app.route('/register-creator', methods=['POST'])
def register_creator():
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        number_of_albums = 0  # Initial value

        # Check if the username already exists in the Creator table
        creator_account_exists = Creator.query.filter_by(username=username).first() is not None

        if creator_account_exists:
            return {
                "status": "error",
                "message": "Username already exists. Choose a different username."
            }

        # If username doesn't exist, create the new creator
        Creator.create_creator(username, password, number_of_albums)

        return {
            "status": "success",
            "message": f"Creator created successfully {username}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"There was an error creating the creator: {e}"
        }


@app.route('/creator-account')
def creator_account():
    
    current_username = session.get('username')  

    return render_template('creatoraccount.html', current_username=current_username)
    


@app.route('/upload-song', methods=['POST'])
def upload_song():
    if request.method == 'POST':
        
        username = request.form.get('username')
        title = request.form.get('title')
        singer = request.form.get('singer')
        album_name = request.form.get('album')
        release_date = request.form.get('release_date')
        lyrics = request.form.get('lyrics')
        genre = request.form.get('genre')
        # Check if the creator exists in the database
        creator = Creator.query.filter_by(username=username).first()

        if not creator:
            return "Creator not found."

        Creator.create_song(creator,title, singer, album_name, release_date, lyrics,genre) 

        return "Song uploaded successfully."

    # Redirect to a different page or handle the case when the request method is not POST
    return render_template('login.html')


@app.route('/check-creator-profile/<username>')

def check_creator_profile(username):
    
    creator = Creator.query.filter_by(username=username).first() 
    if creator:
        total_songs = Song.query.filter_by(creator_id=creator.id).count()
        average_rating = db.session.query(func.avg(Song.rating)).filter_by(creator_id=creator.id).scalar()
        total_albums = Album.query.filter_by(creator_id=creator.id).count()
        albums = Album.query.filter_by(creator_id=creator.id).all()
    
    return render_template('checkcreatorprofile.html', username=username, total_songs=total_songs,average_rating=average_rating, total_albums=total_albums, albums=albums)


@app.route('/album/<album_id>/songs')
def view_album_songs(album_id):
    album = Album.query.get(album_id)
    if album:
        songs = Song.query.filter_by(album_id=album.id).all()
        return render_template('viewalbumsongs.html', album=album, songs=songs)
    
@app.route('/song/<song_id>/edit')
def edit_song(song_id):
    song = Song.query.get(song_id)
    if song:
        return render_template('editsong.html', song=song)


@app.route('/song/<int:song_id>/edit', methods=['POST'])
def update_song(song_id):
    song = Song.query.get(song_id)

    if request.method == 'POST':
        # Get the updated values from the form
        updated_title = request.form.get('title')
        updated_singer = request.form.get('singer')
        updated_release_date_str = request.form.get('release_date')  # Get as string
        updated_lyrics = request.form.get('lyrics')

        # Convert the string date to a Python date object
        updated_release_date = datetime.strptime(updated_release_date_str, '%Y-%m-%d').date()

        # Update the song's attributes
        song.name = updated_title
        song.singer_name = updated_singer
        song.release_date = updated_release_date
        song.lyrics = updated_lyrics

        # Commit the changes to the database
        db.session.commit()

        # Redirect to the view album songs page or another relevant page
        return redirect(url_for('view_album_songs', album_id=song.album_id))

    return render_template('editsong.html', song=song)


@app.route('/song/<int:song_id>/delete', methods=['POST', 'DELETE'])
def delete_song(song_id):
    song = Song.query.get(song_id)

    # Delete the song from the database
    db.session.delete(song)
    db.session.commit()

    # Redirect to the view album songs page or another relevant page
    return redirect(url_for('view_album_songs', album_id=song.album_id))


@app.route('/album/<int:album_id>/delete', methods=['POST', 'DELETE']) 
def delete_album(album_id):
    album = Album.query.get(album_id)

    db.session.delete(album)
    db.session.commit()

    current_username = session.get('username')
        # Redirect to the creator's profile or another relevant page
    return redirect(url_for('check_creator_profile', username=current_username))

@app.route('/adminlogin', methods=['GET', 'POST'])
def admin_login():
    error_message = None

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "abc" and password == "abc": 
            
            return redirect('/admin-dashboard')
        else:
            
            error_message = "Invalid credentials. Please try again."

    return render_template('adminlogin.html', error_message=error_message)


@app.route('/admin-dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    
    albums = Album.query.all()
    total_users = User.query.count()
    total_creators = Creator.query.count()
    total_songs = Song.query.count()
    
    creators = Creator.query.all()
    genres = Song.query.with_entities(Song.genre).distinct().all()
    genre_list = [genre[0] for genre in genres] 
    average_rating_all_songs = db.session.query(func.avg(Song.rating)).scalar()
    
    return render_template('admindashboard.html', albums=albums, total_users=total_users, total_creators=total_creators, total_songs=total_songs,creators=creators,genres=genre_list,average_rating_all_songs=average_rating_all_songs)

@app.route('/admin/remove_creator/<int:creator_id>', methods=['POST', 'DELETE'])
def admin_remove_creator(creator_id):
    creator = Creator.query.get(creator_id)

    if creator:
        # Delete related albums first
        albums = Album.query.filter_by(creator_id=creator.id).all()
        for album in albums:
            db.session.delete(album)

        # Now, delete the creator
        db.session.delete(creator)
        db.session.commit()

    return redirect(url_for('admin_dashboard'))

    
@app.route('/admin/view-album/<int:album_id>/songs')
def admin_view_album_songs(album_id):
    # Fetch data for the specific album
    album = Album.query.get(album_id)
    songs = album.songs

    # Render the template with the fetched data
    return render_template('adminviewalbumsongs.html', album=album, songs=songs)


@app.route('/admin/delete-album/<int:album_id>', methods=['POST', 'DELETE'])
def admin_delete_album(album_id):
    # Fetch the album from the database
    album = Album.query.get(album_id)

    # Perform the deletion
    db.session.delete(album)
    db.session.commit()

    # Redirect to the admin dashboard or another relevant page
    return redirect(url_for('admin_dashboard')) 


@app.route('/admin/view-lyrics/<int:song_id>')
def admin_view_lyrics(song_id):
    # Fetch data for the specific song
    song = Song.query.get(song_id)

    # Render the template with the fetched data
    return render_template('adminviewlyrics.html', song=song) 


@app.route('/admin/delete-song/<int:song_id>/<int:album_id>', methods=['POST', 'DELETE'])
def admin_delete_song(song_id, album_id):
    # Fetch the song from the database
    song = Song.query.get(song_id)

    # Perform the deletion
    db.session.delete(song)
    db.session.commit()

    # Redirect to the admin view album songs page
    return redirect(url_for('admin_view_album_songs', album_id=album_id))


@app.route('/read-lyrics/<int:song_id>')
def read_lyrics(song_id):
    song = Song.query.get(song_id)
    if song:
        return render_template('readlyrics.html', song=song)
    else:
        return "Song not found", 404

@app.route('/add-to-playlist', methods=['POST'])
def add_to_playlist():
    if request.method == 'POST':
        song_id = request.form.get('song_id')

        # Ensure the user is logged in
        if 'username' not in session:
            flash('Please log in to add songs to your playlist.', 'warning')
            return redirect(url_for('login'))  # Redirect to login page or wherever you handle logins

        username = session['username']
        
        # Fetch the song details
        song = Song.query.get(song_id)

        # Fetch existing playlists for the user
        playlists = Playlist.query.filter_by(username=username).all()

        # Render the userplaylist.html template with the required information
        return render_template('userplaylist.html', song=song, playlists=playlists)

    else:
        # Handle non-POST requests (optional)
        return redirect(url_for('login_validation')) 
    
    
@app.route('/add-to-existing-playlist', methods=['POST'])
def add_to_existing_playlist():
    if request.method == 'POST':
        song_id = request.form.get('song_id')
        playlist_id = request.form.get('playlist_id')

        # Fetch the song and playlist
        song = Song.query.get(song_id)
        playlist = Playlist.query.get(playlist_id)

        if song and playlist:
            # Check if the song is already in the playlist
            if song in playlist.songs:
                flash('Song already exists in the playlist.', 'warning')
            else:
                # Add the song to the playlist
                playlist.songs.append(song)
                db.session.commit()
                flash(f'{song.name} added to the playlist successfully!', 'success')

        return redirect(url_for('login_validation'))

    # Handle non-POST requests (optional)
    return redirect(url_for('login_validation'))


@app.route('/create-new-playlist', methods=['POST'])
def create_new_playlist():
    if request.method == 'POST':
        song_id = request.form.get('song_id')
        new_playlist_name = request.form.get('new_playlist_name')

        # Ensure the user is logged in
        if 'username' not in session:
            flash('Please log in to create a new playlist.', 'warning')
            return redirect(url_for('login'))

        username = session['username']

        # Check if the playlist already exists for the user
        existing_playlist = Playlist.query.filter_by(username=username, name=new_playlist_name).first()

        if existing_playlist:
            flash('Playlist with the same name already exists.', 'warning')
        else:
            # Create a new playlist and add the song to it
            new_playlist = Playlist(name=new_playlist_name, username=username)
            db.session.add(new_playlist)

            song = Song.query.get(song_id)
            new_playlist.songs.append(song)

            db.session.commit()
            flash(f'Playlist "{new_playlist_name}" created and {song.name} added successfully!', 'success')

        return redirect(url_for('login_validation'))

    # Handle non-POST requests (optional)
    return redirect(url_for('login_validation'))


@app.route('/user-profile')
def user_profile():
    
    username = session['username']
    playlists = Playlist.query.filter_by(username=username).all()
    return render_template('userprofile.html', username=username, playlists=playlists) 

@app.route('/view-playlist/<int:playlist_id>')
def view_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    songs = playlist.songs
    return render_template('viewplaylist.html', playlist=playlist, songs=songs)


@app.route('/delete-song/<int:playlist_id>/<int:song_id>', methods=['POST'])
def delete_song_from_playlist(playlist_id, song_id):
    
    playlist = Playlist.query.get(playlist_id)

    if playlist.username != session['username']:
        flash('You do not have permission to manage this playlist.', 'danger')
        return redirect(url_for('login_validation'))

    song = Song.query.get(song_id)

    # Remove the song from the playlist
    playlist.songs.remove(song)
    db.session.commit()

    flash('Song deleted from the playlist.', 'success')
    return redirect(url_for('view_playlist', playlist_id=playlist_id))


@app.route('/delete-playlist/<int:playlist_id>', methods=['POST'])
def delete_playlist(playlist_id):
    
    playlist = Playlist.query.get(playlist_id)

    if playlist.username != session['username']:
        flash('You do not have permission to manage this playlist.', 'danger')
        return redirect(url_for('login_validation'))

    # Delete the playlist and its associated songs
    db.session.delete(playlist)
    db.session.commit()

    flash('Playlist deleted successfully.', 'success')
    return redirect(url_for('login_validation'))


@app.route('/user-search')
def user_search():
    return render_template('usersearch.html')


@app.route('/search-for-songs', methods=['GET'])
def search_for_songs():
    search_query = request.args.get('search_query', '')
    search_results = Song.query.filter(or_(Song.name.ilike(f'%{search_query}%'), Song.album.has(Album.album_name.ilike(f'%{search_query}%')))).all()
    return render_template('searchresults.html', search_results=search_results)

@app.route('/search-by-ratings', methods=['GET'])
def search_by_ratings():
    rating_query = request.args.get('rating_query', '')
    search_results = Song.query.filter_by(rating=float(rating_query)).all()
    return render_template('searchresults.html', search_results=search_results)

@app.route('/search-by-genre', methods=['GET'])
def search_by_genre():
    genre_query = request.args.get('genre_query', '')
    search_results = Song.query.filter_by(genre=genre_query).all()
    return render_template('searchresults.html', search_results=search_results)

@app.route('/search-for-albums', methods=['GET'])
def search_for_albums():
    search_query = request.args.get('search_query', '')
    search_results = Album.query.filter(Album.album_name.ilike(f'%{search_query}%')).all()
    return render_template('searchresults.html', search_results=search_results)


@app.route('/rate_song', methods=['POST'])
def rate_song():
    if request.method == 'POST':
        song_id = request.form.get('song_id')
        rating = request.form.get('rating')

        song = Song.query.get(song_id)

        if song:
            # Update the song rating in the database
            song.rating = float(rating) 
            # Save changes to the database
            db.session.commit()

    # Redirect to the page where the user was when they rated the song
    return redirect(request.referrer or '/')



if __name__ == '__main__':
    app.run()

