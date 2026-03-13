from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
import re
import sys
import threading
import webview
import subprocess

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

progress_data = { 'status': 'Idle', 'percent': 0.0, 'speed': '', 'eta': '' }

def get_idm_path():
    paths = [
        r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe",
        r"C:\Program Files\Internet Download Manager\IDMan.exe"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def remove_ansi_colors(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def progress_hook(d):
    if d['status'] == 'downloading':
        progress_data['status'] = 'Downloading...'
        percent_str = remove_ansi_colors(d.get('_percent_str', '0.0%')).strip()
        try: progress_data['percent'] = float(percent_str.replace('%', ''))
        except: progress_data['percent'] = 0.0
        progress_data['speed'] = remove_ansi_colors(d.get('_speed_str', '-')).strip()
        progress_data['eta'] = remove_ansi_colors(d.get('_eta_str', '-')).strip()
    elif d['status'] == 'finished':
        progress_data['status'] = 'Finalizing...'
        progress_data['percent'] = 100.0

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/progress')
def progress(): 
    return jsonify(progress_data)

@app.route('/download', methods=['POST'])
def download():
    progress_data.update({'status': 'Initializing...', 'percent': 0.0, 'speed': '', 'eta': ''})
    urls_text = request.form.get('urls')
    format_type = request.form.get('format_type')
    quality = request.form.get('quality')
    urls = [url.strip() for url in urls_text.split('\n') if url.strip()]

    if not urls: 
        return jsonify({"status": "error", "message": "No links provided."})

    idm_path = get_idm_path()
    downloads_completed = 0

    for url in urls:
        use_idm = False

        if idm_path and format_type == 'video':
            progress_data.update({'status': 'Analyzing link...', 'percent': 30.0})
            try:
                ydl_opts_extract = {
                    'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best',
                    'quiet': True,
                    'noplaylist': True
                }
                with yt_dlp.YoutubeDL(ydl_opts_extract) as ydl:
                    info_best = ydl.extract_info(url, download=False)
                    is_merged = 'requested_formats' in info_best
                    direct_url = info_best.get('url', '')
                    protocol = info_best.get('protocol', '').lower()
                    is_m3u8 = 'm3u8' in protocol or '.m3u8' in direct_url
                    is_dash = 'dash' in protocol or '.mpd' in direct_url
                    
                    if not is_merged and not is_m3u8 and not is_dash and direct_url.startswith('http'):
                        clean_title = re.sub(r'[\\/*?:"<>|]', "", info_best.get('title', 'Video'))
                        ext = info_best.get('ext', 'mp4')
                        filename = f"{clean_title}.{ext}"
                        
                        progress_data.update({'status': 'IDM Started!', 'percent': 100.0})
                        subprocess.Popen([idm_path, '/d', direct_url, '/p', DOWNLOAD_FOLDER, '/f', filename])
                        use_idm = True
                        downloads_completed += 1
            except Exception as e:
                pass

        if not use_idm:
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                'noplaylist': False,
                'quiet': True,
                'progress_hooks': [progress_hook],
                'concurrent_fragment_downloads': 10, 
            }

            if format_type == 'audio':
                ydl_opts.update({'format': 'bestaudio/best', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]})
            else:
                ydl_opts.update({
                    'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best', 
                    'merge_output_format': 'mp4'
                })

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    downloads_completed += 1
            except Exception as e:
                return jsonify({"status": "error", "message": f"Error: {str(e)}"})

    if downloads_completed > 0:
        return jsonify({"status": "success", "message": "All operations completed!"})
    else:
        return jsonify({"status": "error", "message": "Failed to download."})

def start_server():
    app.run(port=5000, use_reloader=False)

if __name__ == '__main__':
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    webview.create_window('YT Downloader', 'http://localhost:5000', width=500, height=750, resizable=True)
    webview.start()