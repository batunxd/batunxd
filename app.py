from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = 'medyaindirici_gizli_anahtar'

DOWNLOAD_FOLDER = '/tmp' 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        format_type = request.form.get('format')
        
        if not url:
            return "Lütfen bir link girin!", 400

        try:
            cookies_path = os.path.abspath('cookies.txt')
            
            # Vercel üzerinde en hafif şekilde çalışacak stabil yt-dlp ayarları
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                'format': 'ba/b' if format_type == 'mp3' else 'best',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                },
            }

            if os.path.exists(cookies_path):
                ydl_opts['cookiefile'] = cookies_path

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                if not os.path.exists(filename):
                    base, _ = os.path.splitext(filename)
                    for ext in ['.mp4', '.m4a', '.webm', '.3gp', '.mkv']:
                        if os.path.exists(base + ext):
                            filename = base + ext
                            break

                if format_type == 'mp3' and not filename.endswith('.mp3'):
                    new_filename = os.path.splitext(filename)[0] + '.mp3'
                    os.rename(filename, new_filename)
                    filename = new_filename

            return send_file(filename, as_attachment=True)

        except Exception as e:
            return f"Bir hata oluştu: {str(e)}", 500

    return render_template('index.html')

# Vercel'in projeyi tanıması için bu satır kritik önem taşıyor
handler = app
