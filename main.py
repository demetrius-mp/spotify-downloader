import os
from pathlib import Path
import sys
from threading import Thread

import click
from dotenv import load_dotenv

from spotify import Spotify
from track import Track


def download_track(track: Track):
    """Downloads the given track. This is used as the thread target.

        Args:
            track (Track): the track to download.
        """

    song_path = f"{track.name}.m4a"
    try:
        if track.video_url is None:
            track.set_youtube_url()

        if os.path.exists(song_path):
            print(f"Skipping {track.name}: Already Downloaded")
            return

        track.download(suppress_exceptions=True)
        track.add_tags()

    except Exception as e:
        if os.path.exists(song_path):
            os.remove(song_path)

        print(f"Error downloading {track.name}: {e}")


@click.command()
@click.option('-i', '--playlist-id', required=True, type=click.STRING,
              help='ID of the playlist you want to download.',
              prompt='Playlist ID:')
@click.option('-p', '--path', default='downloads',
              type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
              help='Path where the tracks will be downloaded.')
def download_playlist(playlist_id: str, path: Path):
    """Downloads the tracks of a Spotify playlist, given it's ID."""

    load_dotenv()
    needed_env = ('SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET', 'SPOTIPY_REDIRECT_URI')
    for env_var in needed_env:
        if not os.environ.get(env_var, None):
            click.echo('Spotify Client ID not found in environment variables.')
            click.echo('Please, provide your credentials in a .env file.')
            sys.exit(0)

    path.mkdir(exist_ok=True)
    os.chdir(path)
    token = Spotify.get_token()
    spotify_client = Spotify(token)
    playlist_tracks = spotify_client.get_playlist_tracks(playlist_id)

    threads = []
    for track in playlist_tracks:
        thread = Thread(target=download_track, args=(track,), daemon=True)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    download_playlist()
