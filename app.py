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
    app_path = os.path.dirname(sys.executable)
else:
    app = Flask(__name__)
    app_path = os.path.dirname(os.path.abspath(__file__))

DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# { video_id: { title, status, percent, speed, eta, done, error } }
downloads = {}
downloads_lock = threading.Lock()

def remove_ansi_colors(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def make_hook(vid_id):
    def progress_hook(d):
        with downloads_lock:
            if vid_id not in downloads:
                return
            if d['status'] == 'downloading':
                downloads[vid_id]['status'] = 'Downloading...'
                percent_str = remove_ansi_colors(d.get('_percent_str', '0.0%')).strip()
                try:
                    downloads[vid_id]['percent'] = float(percent_str.replace('%', ''))
                except:
                    downloads[vid_id]['percent'] = 0.0
                downloads[vid_id]['speed'] = remove_ansi_colors(d.get('_speed_str', '-')).strip()
                downloads[vid_id]['eta'] = remove_ansi_colors(d.get('_eta_str', '-')).strip()
            elif d['status'] == 'finished':
                downloads[vid_id]['status'] = 'Finalizing...'
                downloads[vid_id]['percent'] = 100.0
    return progress_hook

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress')
def progress():
    with downloads_lock:
        return jsonify(downloads)

@app.route('/download', methods=['POST'])
def download():
    urls_text = request.form.get('urls')
    format_type = request.form.get('format_type')
    quality = request.form.get('quality')
    urls = [url.strip() for url in urls_text.split('\n') if url.strip()]

    if not urls:
        return jsonify({"status": "error", "message": "No links provided."})

    # Önce tüm video bilgilerini çek
    all_entries = []
    for url in urls:
        try:
            extract_opts = {
                'quiet': True,
                'noplaylist': False,
                'extract_flat': 'in_playlist',
            }
            with yt_dlp.YoutubeDL(extract_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    for entry in info['entries']:
                        all_entries.append({
                            'url': entry.get('url') or entry.get('webpage_url') or f"https://www.youtube.com/watch?v={entry['id']}",
                            'title': entry.get('title', 'Unknown')
                        })
                else:
                    all_entries.append({
                        'url': url,
                        'title': info.get('title', 'Unknown')
                    })
        except Exception as e:
            all_entries.append({'url': url, 'title': url})

    # downloads dict'i hazırla
    with downloads_lock:
        downloads.clear()
        for i, entry in enumerate(all_entries):
            vid_id = str(i)
            downloads[vid_id] = {
                'title': entry['title'],
                'url': entry['url'],
                'status': 'Waiting...',
                'percent': 0.0,
                'speed': '-',
                'eta': '-',
                'done': False,
                'error': False,
            }

    def run_downloads():
        for i, entry in enumerate(all_entries):
            vid_id = str(i)
            with downloads_lock:
                downloads[vid_id]['status'] = 'Starting...'

            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'quiet': True,
                'progress_hooks': [make_hook(vid_id)],
                'concurrent_fragment_downloads': 10,
                'ffmpeg_location': app_path,
            }

            if format_type == 'audio':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': quality
                    }]
                })
            else:
                ydl_opts.update({
                    'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best',
                    'merge_output_format': 'mp4',
                    'postprocessor_args': {
                        'ffmpeg': ['-c:a', 'aac', '-b:a', '192k']
                    }
                })

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([entry['url']])
                with downloads_lock:
                    downloads[vid_id]['status'] = 'Done'
                    downloads[vid_id]['percent'] = 100.0
                    downloads[vid_id]['done'] = True
            except Exception as e:
                with downloads_lock:
                    downloads[vid_id]['status'] = f'Error: {str(e)}'
                    downloads[vid_id]['error'] = True

    t = threading.Thread(target=run_downloads)
    t.daemon = True
    t.start()

    return jsonify({"status": "success", "count": len(all_entries)})

def start_server():
    app.run(port=5000, use_reloader=False)

if __name__ == '__main__':
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    webview.create_window('YT Downloader', 'http://localhost:5000', width=520, height=800, resizable=True)
    webview.start()