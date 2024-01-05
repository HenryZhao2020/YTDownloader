"""
Contains utilities for configuring and downloading a YouTube video.
"""

import os
import uuid

from pytube import YouTube, Playlist, Stream
import pytube.exceptions as ex


class Option:
    """
    Download options.
    """

    VideoWithAudio = "Video & Audio"
    AudioOnly = "Audio Only"
    VideoOnly = "Video Only"


class Quality:
    """
    Download qualities.
    """

    Highest = "Highest"
    Medium = "Medium"
    Lowest = "Lowest"


def is_url_playlist(url: str) -> bool:
    """
    Checks whether a URL is a YouTube playlist.
    """

    return "playlist" in url


def check_url(url: str) -> str | None:
    """
    Checks whether the specified URL leads to a valid YouTube video/playlist.

    Returns a message if an error occurred.
    """

    if is_url_playlist(url):
        return check_playlist_url(url)
    return check_video_url(url)


def check_video_url(url: str) -> str | None:
    """
    Checks whether the specified URL leads to a valid YouTube video.

    Returns a message if an error occurred.
    """

    try:
        yt = YouTube(url)
        if yt.age_restricted:
            raise ex.AgeRestrictedError(yt.video_id)
        yt.check_availability()
    except ex.RegexMatchError:
        return "Invalid URL!"
    except ex.AgeRestrictedError:
        return "Cannot download an age-restricted video!"
    except ex.LiveStreamError:
        return "Cannot download a live-stream!"
    except ex.VideoPrivate:
        return "Cannot download a private video!"
    except ex.RecordingUnavailable:
        return "No live stream recording available!"
    except ex.MembersOnly:
        return "Cannot download a members-only video!"
    except ex.VideoRegionBlocked:
        return "Video is blocked in your region!"
    except ex.VideoUnavailable:
        return "Video is unavailable!"
    except Exception:
        return "An internal error occurred! Please try again."
    

def check_playlist_url(url: str) -> str | None:
    """
    Checks whether the specified URL leads to a valid YouTube playlist.

    Returns a message if an error occurred.
    """

    try:
        pl = Playlist(url)
        pl.title
        if not pl.videos:
            return "Playlist must not be empty!"
    except Exception:
        return "Invalid URL! Make sure the playlist is public and not empty."


def filter_title(title: str, illegals="<>:\"/\\|?*") -> str:
    """
    Replaces all specified illegal characters with underscores (_).
    """

    for char in illegals:
        title = title.replace(char, "_")

    return title


def get_resolutions(yt: YouTube) -> list[str]:
    """
    Returns all available video resolutions of the specified video.
    """

    streams = yt.streams.filter(only_video=True)
    all_res = {stream.resolution for stream in streams}
    return sorted(all_res, key=lambda res: int(res[:-1]), reverse=True)


def get_bitrates(yt: YouTube) -> list[str]:
    """
    Returns all available audio bitrates of the specified video.
    """

    streams = yt.streams.filter(only_audio=True)
    all_abr = {stream.abr for stream in streams}
    return sorted(all_abr, key=lambda abr: int(abr[:-4]), reverse=True)


def get_file_ext(filename: str) -> str:
    """
    Returns the file extension from the specified file name.
    """

    return os.path.splitext(filename)[1]


def get_quality(quality: str, qualities: list[str]):
    if quality == Quality.Highest:
        return qualities[0]
    if quality == Quality.Medium:
        return qualities[len(qualities) // 2]
    return qualities[-1]


def download_stream(stream: Stream, title: str, folder: str) -> str:
    """
    Downloads a stream based on the specified configuration.
    """
    
    title = filter_title(title)
    ext = get_file_ext(stream.default_filename)
    return stream.download(folder, f"{title}{ext}")


def download_both(yt: YouTube, title: str, res: str, abr: str, folder: str) -> str:
    """
    Downloads a video with audio based on the specified configuration.
    """

    title = filter_title(title)
    video = download_video(yt, f"{title}{uuid.uuid4().hex}", res, folder)
    audio = download_audio(yt, f"{title}{uuid.uuid4().hex}", abr, folder)
    # 'mkv' output container can handle (almost) any codec
    output = os.path.join(folder, f"{title}.mkv")

    ffmpeg(video, audio, output)
    os.remove(video)
    os.remove(audio)

    return output


def download_audio(yt: YouTube, title: str, abr: str, folder: str) -> str:
    """
    Downloads an audio based on the specified configuration.
    """

    stream = yt.streams.filter(only_audio=True, abr=abr)[0]
    return download_stream(stream, title, folder)


def download_video(yt: YouTube, title: str, res: str, folder: str) -> str:
    """
    Downloads a video based on the specified configuration.
    """

    stream = yt.streams.filter(only_video=True, res=res)[0]
    return download_stream(stream, title, folder)


def ffmpeg(video: str, audio: str, output: str):
    """
    Merges the specified video and audio files 
    and outputs them as a single file.
    """

    os.system(f'ffmpeg -i "{video}" -i "{audio}" -c copy "{output}"'
              ' -y -loglevel quiet')


# Download options
OPTIONS = [Option.VideoWithAudio, Option.AudioOnly, Option.VideoOnly]

# Download qualities
QUALITIES = [Quality.Highest, Quality.Medium, Quality.Lowest]
