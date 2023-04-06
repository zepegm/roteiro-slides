import functools
import yt_dlp
import os
from functools import partial

def my_hook(d, obj):
    if d['status'] == 'downloading':
        obj.texto = 'Baixando...'
        #print('Baixando...')
    if d['status'] == 'finished':
        obj.texto = 'Convertendo...'
        #print('Convertendo...')

class ytdlp:
    def __init__(self):
        self.texto = 'Aguardando...'

    def downloadMP3(self, URLS):
        self.texto = 'Iniciando...'
        #URLS = ['https://www.youtube.com/watch?v=ZpeEJaATDBk']
        caminho = os.path.expanduser('~') + '\\Downloads\\Youtube\\'

        ydl_opts = {
            'format': 'mp3/bestaudio/best',
            'outtmpl': caminho + 'audio.%(ext)s',
            'progress_hooks': [functools.partial(my_hook, obj=self)],
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
            self.texto = 'Encerrado...'

        return info
    
    def downloadMP4(self, URLS):
        self.texto = 'Iniciando...'
        #URLS = ['https://www.youtube.com/watch?v=ZpeEJaATDBk']
        caminho = os.path.expanduser('~') + '\\Downloads\\Youtube\\'

        ydl_opts = {
            #'format': 'mp3/bestaudio/best',
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4+best[height<=480]',
            'outtmpl': caminho + 'video.%(ext)s',
            'progress_hooks': [functools.partial(my_hook, obj=self)],
            # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
            #'postprocessors': [{  # Extract audio using ffmpeg
                #'key': 'FFmpegExtractAudio',
                #'preferredcodec': 'mp3',
            #}]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # error_code = ydl.download(URLS)
            info_dict = ydl.extract_info(URLS, download=True)
            titulo = info_dict.get('title').replace('|', '').replace('?', '').replace('\\', '').replace('/', '').replace(':', '').replace('*', '').replace('"', '').strip() + ".mp4"
            caminho = caminho + 'video.mp4'
            info = {'nome':titulo, 'caminho':caminho}
            self.texto = 'Encerrado...'

        return info

    def getText(self):
        return self.texto

