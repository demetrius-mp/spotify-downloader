from __future__ import annotations

import re
from contextlib import suppress
from urllib.request import urlopen

import pafy
import requests
from mutagen.mp4 import MP4, MP4Cover


class Track:
    """Stores and retrieves information of a track.
        This class is responsible to:
         - get the YouTube URL of a track, using it's name.
         - add the metadata tags of a track.
    """

    invalid_track_name_characters = r"[#<%>&\*\{\?\}/\\$+!`'\|\"=@\.\[\]:]*"

    def __init__(self, title: str, artist: str, album: str, album_img_url: str, video_url: str = None) -> None:
        """
        Args:
            title (str): title of the song
            artist (str): artist of the song
            album (str): album of the song
            album_img_url (str): url of the album image
            video_url (str, optional): url of the video. Defaults to None.
        """

        self.title = title
        self.artist = artist
        self.album = album
        self.album_img_url = album_img_url
        self.video_url = video_url
        self._name = None

    @property
    def name(self):
        if self._name is None:
            self._name = re.sub(Track.invalid_track_name_characters, "", f'{self.artist} {self.title}')

        return self._name

    def set_youtube_url(self):
        """Get's the youtube url of this track, using it's name.

        Returns:
            str | None: the url, if it's found. None otherwise.
        """

        base_url = 'https://www.youtube.com'

        # replaces ' ' with '+'
        track_name = self.name.replace(' ', '+').encode('utf-8')
        search_url = f"{base_url}/results?search_query={track_name}"
        html = urlopen(search_url).read().decode()
        video_ids = re.findall(r"watch\?v=(\S{11})", html)
        if video_ids:
            self.video_url = f"{base_url}/watch?v={video_ids[0]}"
            return self.video_url

        return None

    @staticmethod
    def __download(url: str, name: str):
        vid = pafy.new(url)
        vid.getbestaudio(preftype='m4a').download(f"{name}.m4a")

    def download(self, suppress_exceptions: bool = False) -> None:
        if suppress_exceptions:
            with suppress(Exception):
                Track.__download(self.video_url, self.name)

        else:
            Track.__download(self.video_url, self.name)

    def add_tags(self):
        """Adds metadata tags to the track, like title, album, artist, and cover art"""
        title_key = "\xa9nam"
        album_key = "\xa9alb"
        artist_key = "\xa9ART"
        art_key = "covr"

        f = MP4(f'{self.name}.m4a')
        f[title_key] = self.title
        f[album_key] = self.album
        f[artist_key] = self.artist
        res = requests.get(self.album_img_url)
        f[art_key] = [MP4Cover(res.content, MP4Cover.FORMAT_JPEG)]

        f.save()

    @classmethod
    def __from_dict(cls, dic: dict) -> Track | None:
        track = dic['track'] if 'track' in dic else dic
        album = track['album']['name']
        artist = track['artists'][0]['name']
        title = track['name']
        print(track)
        album_img_url = track['album']['images'][0]['url']

        return cls(
            title=title,
            artist=artist,
            album=album,
            album_img_url=album_img_url
        )

    @classmethod
    def from_dict(cls, dic: dict, suppress_exceptions: bool = False) -> Track | None:
        if suppress_exceptions:
            with suppress(Exception):
                return cls.__from_dict(dic)

        else:
            return cls.__from_dict(dic)
