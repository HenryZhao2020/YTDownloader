"""
Contains utilities for configuring and downloading a YouTube video.
"""

import os
import uuid
from urllib.error import HTTPError

import pytube.exceptions as ex
from pytube import YouTube, Playlist, Stream


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


def isUrlPlaylist(url: str) -> bool:
    """
    Checks whether a URL is a YouTube playlist.
    """

    return "playlist" in url


def checkUrl(url: str) -> str | None:
    """
    Checks whether the specified URL is a valid YouTube video or playlist.

    Returns a text message if an error occurred; otherwise, return None.
    """

    if isUrlPlaylist(url):
        return checkPlaylistUrl(url)

    return checkVideoUrl(url)


def checkVideoUrl(url: str) -> str | None:
    """
    Checks whether the specified URL is a valid YouTube video.

    Returns a text message if an error occurred; otherwise, return None.
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
    except ex.PytubeError:
        return "An internal error occurred! Please try again."
    

def checkPlaylistUrl(url: str) -> str | None:
    """
    Checks whether the specified URL is a valid YouTube playlist.

    Returns a text message if an error occurred; otherwise, return None.
    """

    try:
        pl = Playlist(url)
        if pl.title and not pl.videos:
            return "Playlist must not be empty!"
    except (KeyError, HTTPError):
        return "Invalid URL! Make sure the playlist is public and not empty."


def isVideoInPlaylist(url: str) -> bool:
    """
    Checks whether a video is part of a playlist.
    """

    return "list" in url


def extractPlaylistUrl(url: str) -> str:
    """
    Attempts to extract the playlist URL from a video URL.
    """

    if isVideoInPlaylist(url):
        id = url[url.index("list"):]
        return f"https://www.youtube.com/playlist?{id}"
    
    return url


def filterTitle(title: str, illegals="<>:\"/\\|?*") -> str:
    """
    Replaces all specified illegal characters with underscores (_).
    """

    for char in illegals:
        title = title.replace(char, "_")

    return title


def allResolutions(yt: YouTube) -> list[str]:
    """
    Returns all available video resolutions of the specified video.
    """

    # All video streams
    streams = yt.streams.filter(only_video=True)
    # Unsorted resolutions of the video streams
    allRes = {stream.resolution for stream in streams}
    # Sort based on the integer part (without the ending 'p')
    return sorted(allRes, key=lambda res: int(res[:-1]), reverse=True)


def allBitrates(yt: YouTube) -> list[str]:
    """
    Returns all available audio bitrates of the specified video.
    """

    # All audio streams
    streams = yt.streams.filter(only_audio=True)
    # Unsorted bitrates of the audio streams
    allAbr = {stream.abr for stream in streams}
    # Sort based on the integer part (without the ending 'kbps')
    return sorted(allAbr, key=lambda abr: int(abr[:-4]), reverse=True)


def getResolution(yt: YouTube, quality: str) -> str:
    """
    Returns the video resolution that corresponds to the specified quality.
    """

    # If the specified quality is custom, return the custom quality
    if quality not in QUALITIES:
        return quality

    allRes = allResolutions(yt)

    # Otherwise, return the video resolution that corresponds to
    # 'Highest', 'Medium' or 'Lowest'
    if quality == Quality.Highest:
        index = 0
    elif quality == Quality.Medium:
        index = len(allRes) // 2 + len(allRes) % 2
    else:
        index = -1

    return allRes[index]


def getBitrate(yt: YouTube, quality: str) -> str:
    """
    Returns the audio bitrate that corresponds to the specified quality.
    """

    # If the specified quality is custom, return the custom quality
    if quality not in QUALITIES:
        return quality

    allAbr = allBitrates(yt)

    # Otherwise, return the audio bitrate that corresponds to
    # 'Highest', 'Medium' or 'Lowest'
    if quality == Quality.Highest:
        index = 0
    elif quality == Quality.Medium:
        index = len(allAbr) // 2 + len(allAbr) % 2
    else:
        index = -1

    return allAbr[index]


def getFileExt(filename: str) -> str:
    """
    Returns the file extension of the specified file name.
    """

    return os.path.splitext(filename)[1]


def downloadStream(stream: Stream, title: str, dir: str) -> str:
    """
    Downloads a stream based on the specified configuration.
    """
    
    title = filterTitle(title)
    ext = getFileExt(stream.default_filename)
    return stream.download(dir, f"{title}{ext}")


def downloadVideo(yt: YouTube, title: str, res: str, dir: str) -> str:
    """
    Downloads a video based on the specified configuration.
    """

    stream = yt.streams.filter(only_video=True, res=res)[0]
    return downloadStream(stream, title, dir)


def downloadAudio(yt: YouTube, title: str, abr: str, dir: str) -> str:
    """
    Downloads an audio based on the specified configuration.
    """

    stream = yt.streams.filter(only_audio=True, abr=abr)[0]
    return downloadStream(stream, title, dir)


def downloadBoth(yt: YouTube, title: str, res: str, abr: str, dir: str) -> str:
    """
    Downloads a video with audio based on the specified configuration.
    """

    title = filterTitle(title)
    # Path of the downloaded video stream
    video = downloadVideo(yt, f"{title}{uuid.uuid4().hex}", res, dir)
    # Path of the downloaded audio stream
    audio = downloadAudio(yt, f"{title}{uuid.uuid4().hex}", abr, dir)
    # Path of the output file
    # 'mkv' output container can handle (almost) any codec
    output = os.path.join(dir, f"{title}.mkv")

    # Merge the video and audio with ffmpeg
    ffmpeg(video, audio, output)
    # Remove the temporary files
    os.remove(video)
    os.remove(audio)

    return output


def ffmpeg(video: str, audio: str, output: str):
    """
    Merges the specified video and audio files 
    and outputs them as a single file.
    """

    os.system(f'ffmpeg -i "{video}" -i "{audio}" -c copy "{output}"'
              ' -y -loglevel quiet')


# Download options
OPTIONS = [
    Option.VideoWithAudio,
    Option.AudioOnly,
    Option.VideoOnly
]

# Download qualities
QUALITIES = [
    Quality.Highest,
    Quality.Medium,
    Quality.Lowest
]
