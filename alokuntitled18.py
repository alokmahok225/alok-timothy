import os
from flask import Flask, request, render_template_string
import google.generativeai as genai

app = Flask(__name__)

# --- GANTI DENGAN KUNCI API GEMINI ANDA DI SINI ---
# Pastikan tidak ada spasi di awal atau akhir kunci
# Disarankan untuk menggunakan variabel lingkungan untuk kunci API Anda
# Contoh: GEMINI_API_KEY = os.getenv("YOUR_GEMINI_API_KEY")
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY" # <--- GANTI INI DENGAN KUNCI API ANDA
genai.configure(api_key=GEMINI_API_KEY)

# Inisialisasi model Gemini
model = genai.GenerativeModel('gemini-pro')

# Template HTML untuk antarmuka web
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rekomendasi Klip YouTube AI</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(to right, #ece9e6, #ffffff);
            color: #333;
            display: flex;
            justify-content: center;
            align-items: flex-start; /* Mengubah center ke flex-start */
            min-height: 100vh;
            box-sizing: border-box;
        }
        .container {
            width: 100%;
            max-width: 700px;
            background: #fff;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 6px 15px rgba(0,0,0,0.1);
            animation: fadeIn 0.8s ease-out;
            border: 1px solid #e0e0e0;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h1 {
            color: #007bff;
            text-align: center;
            margin-bottom: 25px;
            font-size: 2em;
            letter-spacing: 0.5px;
        }
        .info {
            background-color: #e6f7ff;
            color: #0056b3;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 25px;
            border: 1px solid #b3e0ff;
            font-size: 0.95em;
            line-height: 1.5;
        }
        .info ul {
            padding-left: 20px;
            margin-top: 10px;
        }
        .info li {
            margin-bottom: 5px;
        }
        textarea {
            width: calc(100% - 22px); /* Penyesuaian lebar untuk padding/border */
            padding: 11px;
            margin-bottom: 15px;
            border: 1px solid #ccd;
            border-radius: 6px;
            resize: vertical;
            min-height: 80px;
            font-size: 1em;
            box-sizing: border-box; /* Pastikan padding masuk hitungan width */
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1.1em;
            width: 100%;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #0056b3;
        }
        .response {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 25px;
            white-space: pre-wrap; /* Mempertahankan format teks dari Gemini */
            word-wrap: break-word; /* Memastikan teks panjang tidak keluar wadah */
            border: 1px solid #e9ecef;
            line-height: 1.6;
            font-size: 0.95em;
            color: #555;
        }
        .response strong {
            color: #007bff;
            display: block;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        a {
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        @media (max-width: 600px) {
            body { padding: 10px; }
            .container { padding: 15px; }
            h1 { font-size: 1.8em; }
            button { font-size: 1em; padding: 10px 15px; }
            .info, .response { font-size: 0.9em; padding: 12px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Rekomendasi Klip YouTube AI</h1>
        <div class="info">
            <p>Ketik perintah Anda di bawah ini:</p>
            <ul>
                <li>Untuk obrolan biasa dengan Gemini: <code>/ai: [pertanyaan Anda]</code></li>
                <li>Untuk rekomendasi klip YouTube: <code>/ai/clip: [link YouTube]</code></li>
            </ul>
            <p>Contoh: <code>/ai/clip: https://www.youtube.com/watch?v=dQw4w9WgXcQ</code></p>
            <p>Jika tanpa awalan, akan muncul pemberitahuan dan penjelasan singkat.</p>
        </div>
        <form method="POST">
            <textarea name="user_input" placeholder="Ketik perintah Anda di sini...">{{ user_input if user_input else '' }}</textarea><br>
            <button type="submit">Kirim</button>
        </form>
        {% if response %}
            <div class="response">
                <strong>Hasil:</strong><br>
                {{ response }}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

# Konfigurasi aplikasi web Flask
@app.route('/', methods=['GET', 'POST'])
def index():
    user_input = ""
    response_text = ""
    if request.method == 'POST':
        user_input = request.form['user_input'].strip()

        if user_input.startswith("/ai:"):
            prompt = user_input[len("/ai:"):].strip()
            if prompt:
                try:
                    response = model.generate_content(prompt)
                    response_text = response.text
                except Exception as e:
                    response_text = f"Maaf, terjadi kesalahan saat menghubungi Gemini untuk obrolan: {e}"
            else:
                response_text = "Mohon masukkan pertanyaan Anda setelah '/ai:'"

        elif user_input.startswith("/ai/clip:"):
            youtube_link = user_input[len("/ai/clip:"):].strip()
            if youtube_link:
                # Prompt khusus untuk rekomendasi klip TikTok
                clip_prompt = f"""
                Berdasarkan video YouTube ini: {youtube_link}, buatlah rekomendasi 3-5 segmen klip singkat (maksimal 60 detik per klip) yang efektif untuk TikTok.
                Fokus pada bagian-bagian yang memiliki 'hook' kuat, momen menarik, viral, atau poin penting yang relevan dengan tren TikTok saat ini.
                Untuk setiap rekomendasi, berikan:
                - **Durasi/Timestamp:** (misal: 0:35 - 1:15)
                - **Penjelasan Singkat Klip:** Apa yang terjadi di segmen ini.
                - **Alasan Efektif untuk TikTok:** Jelaskan mengapa klip ini berpotensi menarik perhatian di TikTok (misal: "momen lucu", "informasi penting", "transisi visual menarik", "dialog inspiratif", "ekspresi unik", "reaksi emosional", "konten POV yang relate", dll. Sesuaikan dengan gaya dan kecepatan TikTok).
                
                Pastikan format jawabannya mudah dibaca per poin, gunakan bullet point atau numbering untuk setiap rekomendasi.
                """
                try:
                    response = model.generate_content(clip_prompt)
                    response_text = response.text
                except Exception as e:
                    response_text = f"Maaf, terjadi kesalahan saat menghasilkan rekomendasi klip: {e}"
            else:
                response_text = "Mohon masukkan link YouTube setelah '/ai/clip:'"
        else:
            # Pesan pemberitahuan jika tidak ada awalan yang cocok
            response_text = """
            **Perintah Tidak Dikenal.**
            
            Silakan gunakan salah satu awalan berikut untuk berinteraksi:
            
            -   `/ai: [pertanyaan Anda]`
                * Contoh: `/ai: Ceritakan tentang sejarah internet.`
                * Fungsi: Akan membuka obrolan biasa dengan Gemini, menjawab pertanyaan umum atau memberikan informasi.
            
            -   `/ai/clip: [link YouTube]`
                * Contoh: `/ai/clip: https://www.youtube.com/watch?v=dQw4w9WgXcQ`
                * Fungsi: Akan menganalisis video YouTube dari link yang Anda berikan dan membuat rekomendasi menit-menit klip pendek yang efektif untuk diunggah ke TikTok, lengkap dengan penjelasan singkat dan alasan mengapa klip tersebut menarik.
            
            Yuk, coba lagi!
            """
    return render_template_string(HTML_TEMPLATE, response=response_text, user_input=user_input)

# Jalankan aplikasi Flask
if __name__ == '__main__':
    # '0.0.0.0' sangat penting agar aplikasi bisa diakses dari luar localhost (dari internet)
    # Port 5000 adalah port standar yang sering digunakan untuk pengembangan Flask
    app.run(host='0.0.0.0', port=5000)
