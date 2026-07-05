from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = 'medyaindirici_telefon_anahtari'

# Termux içinde projenin çalıştığı klasörün altında 'downloads' adında bir klasör oluşturur
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        format_type = request.form.get('format')
        
        if not url:
            return "Lütfen bir link girin!", 400

        try:
            # Telefon sunucusunda artık ham indirme yapacağımız için karmaşık ayarlara gerek yok
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                },
            }

            # Telefonuna kuracağımız ffmpeg sayesinde ses ve videoları kusursuz işleyebiliriz
            if format_type == 'mp3':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            else:
                # Video ve sesi en yüksek kalitede ayrı indirip arka planda otomatik birleştirir
                ydl_opts['format'] = 'bestvideo+bestaudio/best'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Eğer mp3 dönüşümünden sonra uzantı güncellenmediyse koddaki ismini düzeltelim
                if format_type == 'mp3' and not filename.endswith('.mp3'):
                    base, _ = os.path.splitext(filename)
                    filename = base + '.mp3'

            # İndirilen dosyayı kullanıcının tarayıcısına gönderiyoruz
            return send_file(filename, as_attachment=True)

        except Exception as e:
            return f"Bir hata oluştu: {str(e)}", 500

    return render_template('index.html')

if __name__ == '__main__':
    # Termux yerel ağda çalışacağı için host'u 0.0.0.0 yapıyoruz ki ağdaki diğer cihazlar da görebilsin
    app.run(host='0.0.0.0', port=5000, debug=True)
    
