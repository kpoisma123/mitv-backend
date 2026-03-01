import yt_dlp
import requests
import json
import os
from github import Github

# ─── CONFIGURACIÓN ───────────────────────────────────────────────
GITHUB_TOKEN = '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'
GITHUB_REPO = 'kpoisma123/mitv-config'
CONFIG_FILE = 'config.json'

def obtener_stream_url(video_id):
    if not video_id:
        return ''
    url = f'https://www.youtube.com/watch?v={video_id}'
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best[ext=mp4]/best',
        'extract_flat': False,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info.get('url', '')
            print(f'✅ {info.get("title", video_id)}: OK')
            return stream_url
    except Exception as e:
        print(f'❌ Error con {video_id}: {e}')
        return ''

def actualizar_config():
    # Descargar config actual de GitHub
    config_url = f'https://raw.githubusercontent.com/{GITHUB_REPO}/main/{CONFIG_FILE}'
    response = requests.get(config_url)
    config = response.json()

    # Procesar canales principales
    for canal in config['canales']['principales']:
        if not canal.get('bloqueado', False) and canal.get('video_id'):
            stream_url = obtener_stream_url(canal['video_id'])
            canal['stream_url'] = stream_url

    # Procesar canales infantiles
    for canal in config['canales']['infantiles']:
        if not canal.get('bloqueado', False) and canal.get('video_id'):
            stream_url = obtener_stream_url(canal['video_id'])
            canal['stream_url'] = stream_url

    # Subir config actualizado a GitHub
    if GITHUB_TOKEN:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        contents = repo.get_contents(CONFIG_FILE)
        repo.update_file(
            CONFIG_FILE,
            'Actualizar stream URLs',
            json.dumps(config, indent=2, ensure_ascii=False),
            contents.sha
        )
        print('✅ Config actualizado en GitHub')
    else:
        # Si no hay token, guardar local para probar
        with open('config_actualizado.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print('✅ Config guardado localmente en config_actualizado.json')

if __name__ == '__main__':
    print('🚀 Iniciando actualización de streams...')
    actualizar_config()
    print('✅ Proceso terminado')
    