import yt_dlp
import os

def downloadMP3(URLS):
    #URLS = ['https://www.youtube.com/watch?v=ZpeEJaATDBk']
    caminho = os.path.expanduser('~') + '\\Downloads\\Youtube\\'

    ydl_opts = {
        'format': 'mp3/bestaudio/best',
        'outtmpl': caminho + 'audio.%(ext)s',
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # error_code = ydl.download(URLS)
        info_dict = ydl.extract_info(URLS, download=True)
        titulo = info_dict.get('title').replace('|', '').replace('?', '').replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('"', '').strip() + ".mp3"
        caminho = caminho + 'audio.mp3'
        info = {'nome':titulo, 'caminho':caminho}

    return info