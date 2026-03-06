from flask import Flask, render_template, request, jsonify
import yt_dlp
import os
import re
import sys
import threading
import webview

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    app = Flask(__name__, template_folder=template_folder)
else:
    app = Flask(__name__)

DOWNLOAD_FOLDER = r'C:\Users\alper\Downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

progress_data = { 'status': 'Idle', 'percent': 0.0, 'speed': '', 'eta': '' }

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

    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'noplaylist': False,
        'quiet': True,
        'progress_hooks': [progress_hook],
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
            ydl.download(urls)
        return jsonify({"status": "success", "message": "All downloads completed!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error: {str(e)}"})

def start_server():
    app.run(port=5000, use_reloader=False)

if __name__ == '__main__':
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    # Updated title to "YT Downloader"
    webview.create_window('YT Downloader', 'http://localhost:5000', width=500, height=750, resizable=False)
    webview.start()