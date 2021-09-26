from typing import Iterator

import requests
from spotipy import SpotifyOAuth

from track import Track


class Spotify:
    def __init__(self, token: str) -> None:
        """

        Args:
            token: an access token. Use Spotify.get_token() to get one.
        """
        self.token = token

    @staticmethod
    def get_token() -> str:
        """Uses `spotipy.SpotifyOAuth` flow to get an access token.
        Requires the following environment variables:
          - SPOTIPY_CLIENT_ID: Spotify API client ID.
          - SPOTIPY_CLIENT_SECRET: Spotify API client secret.
          - SPOTIPY_REDIRECT_URI: Spotify API redirect URI.

        Returns: the token.

        """
        auth_manager = SpotifyOAuth(scope='user-library-read')
        return auth_manager.get_access_token(as_dict=False)

    def get_playlist_tracks(self, playlist_id: str, limit: int = 10000) -> Iterator[Track]:
        """Uses Spotify API to retrieve the tracks of a playlist, given it's ID.

        Args:
            playlist_id (str): id of the playlist.
            limit (int, optional): the number of tracks to retrieve. Defaults to 10000.

        Yields:
            Iterator[Track]: generator object that yields the tracks.
        """
        offset = 0
        fetched = 0

        headers = {
            "Content-Type": "application/json",
            "Authorization": f'Bearer {self.token}'
        }

        while offset < limit:
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}&limit=50"
            response = requests.get(
                url=url,
                headers=headers
            )

            results = response.json()
            if not response.ok:
                break

            if "items" not in results or not results["items"]:
                return

            for item in results['items']:
                fetched += 1
                song = Track.from_dict(item, suppress_exceptions=True)
                yield song

                if fetched >= limit:
                    return

            offset += 50
