# spotipy-dl

CLI tool to download Spotify playlists with metadata.

## Initial configuration
### 1. Create a developer Spotify App.
Go to the [Spotify developer's dashboard](https://developer.spotify.com/dashboard/applications)
and create an app.

Click `Edit settings`

Add the following `Redirect URI`: http://localhost:8888/callback

If the port :8888 is in use, please change to one that's not in use.

You will need the` Client ID` and the `Client secret` for the next step.

### 2. Environment configuration
**Note: It's higly recommended that you create a virtual environment for this
tool.**

Create a .env file in the root directory and paste the following lines:
```
SPOTIPY_CLIENT_ID=<your client id>
SPOTIPY_CLIENT_SECRET=<your client secret>
SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
```
**Note: use the same port you used as the Redirect URI for your Spotify App.**

## How to use the tool
The CLI help is already a good guide on how to use the tool.
To access it, type the following command while in the root directory:
```
python main.py --help
```

## How it works
1. Using [spotipy](https://github.com/plamere/spotipy), we get the access token to the API.

2. With the token, we retrieve the playlist's tracks, storing the following informations:
    title, artist, album, album image URL.

    **Note: to be more efficient, this is done yielding each track retrieved**

3. Then, using [urllib](https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen),
    we query for the track title and artist in YouTube.
    
    **Note: as of today, all it does is to return the first video URL found. Check this [issue]() for more information**

4. With the video URL, we use [pafy](https://github.com/mps-youtube/pafy) to download the track from the best audio stream.

5. Using [mutagen](https://github.com/quodlibet/mutagen) we set the audio metadata, including the cover art,
which is retrieved using [requests](https://docs.python-requests.org/en/latest/) module, 
by requesting the album image URL attribute of the track.

6. For faster processing, we use the 
[threading](https://docs.python.org/3/library/threading.html#threading.Thread) module, creating a `Thread`
object for each track.
