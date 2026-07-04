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
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
            }

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
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                if format_type == 'mp3':
                    filename = os.path.splitext(filename)[0] + '.mp3'

            return send_file(filename, as_attachment=True)

        except Exception as e:
            return f"Bir hata oluştu: {str(e)}", 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)