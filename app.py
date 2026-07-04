from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import ffbinaries

app = Flask(__name__)
app.secret_key = 'medyaindirici_gizli_anahtar'

DOWNLOAD_FOLDER = '/tmp' # İnternet sunucularında yazma izni olan geçici klasör
FFMPEG_FOLDER = '/tmp/ffmpeg_bin'

# Sunucu ayağa kalkarken ffmpeg yoksa otomatik indiriyoruz
if not os.path.exists(os.path.join(FFMPEG_FOLDER, 'ffmpeg')):
    os.makedirs(FFMPEG_FOLDER, exist_ok=True)
    print("FFmpeg sunucuya indiriliyor...")
    ffbinaries.download_binaries(['ffmpeg', 'ffprobe'], download_path=FFMPEG_FOLDER)
    # Çalıştırma izinlerini veriyoruz
    os.chmod(os.path.join(FFMPEG_FOLDER, 'ffmpeg'), 0o755)
    os.chmod(os.path.join(FFMPEG_FOLDER, 'ffprobe'), 0o755)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        format_type = request.form.get('format')
        
        if not url:
            return "Lütfen bir link girin!", 400

        try:
            cookies_path = os.path.abspath('cookies.txt')
            
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                # İndirdiğimiz ffmpeg klasörünü yt-dlp'ye gösteriyoruz:
                'ffmpeg_location': FFMPEG_FOLDER,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Sec-Fetch-Mode': 'navigate',
                },
            }

            if os.path.exists(cookies_path):
                ydl_opts['cookiefile'] = cookies_path

            if format_type == 'mp3':
                # FFmpeg geldiği için artık sesi kusursuzca MP3'e çevirebiliriz!
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            else:
                # En yüksek kalitede video ve sesi ayrı indirip otomatik birleştirecek
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # FFmpeg mp3 dönüştürmesi sonrası uzantıyı kontrol edelim
                if format_type == 'mp3' and not filename.endswith('.mp3'):
                    base, _ = os.path.splitext(filename)
                    filename = base + '.mp3'

            return send_file(filename, as_attachment=True)

        except Exception as e:
            return f"Bir hata oluştu: {str(e)}", 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
