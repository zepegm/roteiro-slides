import yt_dlp
import os

def downloadMP3(URLS):
    #URLS = ['https://www.youtube.com/watch?v=ZpeEJaATDBk']
    caminho = os.path.expanduser('~') + '\\Downloads\\Youtube\\'

    ydl_opts = {
        'format': 'mp3/bestaudio/best',
        'outtmpl': caminho + '%(title)s.%(ext)s',
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # error_code = ydl.download(URLS)
        info_dict = ydl.extract_info(URLS, download=True)
        caminho = caminho + info_dict.get('title', None) + ".mp3"

    return caminho