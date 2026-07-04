from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = 'medyaindirici_gizli_anahtar'

DOWNLOAD_FOLDER = '/tmp' # İnternet sunucularında yazma izni olan geçici klasör

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
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                # Sunucuda ffmpeg hatası çıkmasını önlemek için harici birleştiricileri kapatıyoruz
                'prefer_ffmpeg': False,
            }

            if os.path.exists(cookies_path):
                ydl_opts['cookiefile'] = cookies_path

            if format_type == 'mp3':
                # En yüksek kalitedeki hazır ses formatını direkt indir
                ydl_opts.update({
                    'format': 'bestaudio',
                })
            else:
                # Video ve sesi hazır birleşik halde barındıran en iyi tek parça formatı indirir (Hata riskini sıfırlar)
                ydl_opts.update({
                    'format': 'best',
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Eğer mp3 seçildiyse ve dosya uzantısı farklıysa sunucuda isimlendirmeyi düzeltelim
                if format_type == 'mp3' and not filename.endswith('.mp3'):
                    base, _ = os.path.splitext(filename)
                    os.rename(filename, base + '.mp3')
                    filename = base + '.mp3'

            return send_file(filename, as_attachment=True)

        except Exception as e:
            return f"Bir hata oluştu: {str(e)}", 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
