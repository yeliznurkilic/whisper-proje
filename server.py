from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import whisper
import os
import subprocess
import uuid
import asyncio
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from telegram import Bot
from telegram.ext import Application


# Whisper model (medium)
whisper_model = whisper.load_model("medium")

# Konu tespiti modeli
TOPIC_MODEL_PATH = "models/topic_model_final"
topic_tokenizer = AutoTokenizer.from_pretrained(TOPIC_MODEL_PATH, use_fast=False)
topic_model = AutoModelForSequenceClassification.from_pretrained(TOPIC_MODEL_PATH)
topic_classifier = pipeline("text-classification", model=topic_model, tokenizer=topic_tokenizer)

# Telegram bot token ve chat_id
bot_token = "telegram_tokenını_buraya_yaz"
chat_id = "6695817972" 

async def send_telegram_notification(title, message):
    try:
        bot = Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=f"{title}\n{message}")
    except Exception as e:
        print(f"Telegram bildirimi gönderilemedi: {e}")


#HTTP HANDLER
class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        html = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Whisper AI</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: #e5e7eb;
    padding: 20px;
}
.container {
    max-width: 600px;
    margin: auto;
}
input, select, button {
    width: 100%;
    padding: 14px;
    margin-top: 12px;
    font-size: 16px;
    border-radius: 8px;
    border: none;
}
button {
    background: #2563eb;
    color: white;
}
.card {
    background: #020617;
    margin-top: 16px;
    padding: 16px;
    border-radius: 10px;
}
.badge {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 6px;
    background: #334155;
    margin-right: 6px;
}
.loading {
    text-align: center;
    margin-top: 20px;
}
</style>
</head>
<body>

<div class="container">
<h2>Lütfen ses dosyanızı yükleyin veya ses kaydedin</h2>

<form method="POST" enctype="multipart/form-data" onsubmit="showLoading()">
    <input type="file" name="audio" accept="audio/*" required>

    <label>Çeviri yapılsın mı?</label>
    <select name="translate" id="translate" onchange="toggleLang()">
        <option value="no">Hayır</option>
        <option value="yes">Evet</option>
    </select>

    <label>Hedef dil:</label>
    <select name="target_lang" id="target_lang">
        <option value="en">İngilizce</option>
        <option value="tr">Türkçe</option>
    </select>

    <button type="submit">Analizi Başlat</button>
</form>

<div id="loading" class="loading" style="display:none;">
⏳ Ses işleniyor, lütfen bekleyin...
</div>

</div>

<script>
function toggleLang() {
    const show = document.getElementById("translate").value === "yes";
    document.getElementById("target_lang").style.display = show ? "block" : "none";
}
function showLoading() {
    document.getElementById("loading").style.display = "block";
}
</script>

</body>
</html>
"""
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD": "POST"}
        )

        if "audio" not in form:
            self.send_response(400)
            self.end_headers()
            return

        file_item = form["audio"]
        translate = form.getvalue("translate", "no")
        target_lang = form.getvalue("target_lang", "en")  # Kullanıcıdan seçilen hedef dil (İngilizce veya Türkçe)

        uid = str(uuid.uuid4())
        input_file = f"{uid}_{file_item.filename}"
        wav_file = f"{uid}.wav"

        # Dosya formatı kontrolü
        if not file_item.filename.endswith(('.mp3', '.wav', '.webm', '.m4a')):
            self.send_response(400)
            self.end_headers()
            self.wfile.write("Desteklenmeyen dosya formatı. Lütfen .mp3, .wav, .webm veya .m4a dosya yükleyin.".encode("utf-8"))
            return

        with open(input_file, "wb") as f:
            f.write(file_item.file.read())

        # Eğer dosya M4A formatında ise, dönüştürme işlemi yapalım
        if input_file.endswith(".m4a"):
            subprocess.run(
                ["ffmpeg", "-y", "-i", input_file, wav_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # Diğer ses formatlarında direk kaydedelim
            subprocess.run(
                ["ffmpeg", "-y", "-i", input_file, wav_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        # 1️⃣ Orijinal metin + otomatik dil
        original = whisper_model.transcribe(wav_file, task="transcribe")
        original_text = original["text"].strip()
        detected_lang = original["language"]

        # 2️⃣ Konu tespiti
        topic = topic_classifier(original_text)[0]
        topic_label = topic["label"]
        topic_score = round(topic["score"], 3)

        translated_block = ""

        # 3️⃣ Çeviri istenirse ve hedef dil belirlenmişse
        if translate == "yes":
            # target_lang'i doğru bir şekilde geçirelim
            if target_lang == "en":
                translated = whisper_model.transcribe(
                    wav_file,
                    task="translate",
                    language="en"  # İngilizce çeviri
                )
            elif target_lang == "tr":
                translated = whisper_model.transcribe(
                    wav_file,
                    task="translate",
                    language="tr"  # Türkçe çeviri
                )
            translated_block = f"""
<div class="card">
<h3>🌐 Çevrilen Metin ({target_lang})</h3>
<p>{translated["text"].strip()}</p>
</div>
"""

        os.remove(input_file)
        os.remove(wav_file)

        # Sonuçları HTML olarak döndür
        response = f"""
<div class="card">
<span class="badge">🌍 Dil: {detected_lang}</span>
<span class="badge">🧠 Konu: {topic_label} ({topic_score})</span>
</div>

<div class="card">
<h3>📝 Orijinal Metin</h3>
<p>{original_text}</p>
</div>

{translated_block}
"""

        # Bildirim Gönder (Telegram)
        title = "Yeni Konu ve Çeviri Sonucu"
        message = f"Yeni konu: {topic_label}\nDil: {detected_lang}\nOrijinal Metin: {original_text}"

        # Telegram bildirim gönder (Asenkron)
        try:
            asyncio.run(send_telegram_notification(title, message))
        except Exception as e:
            print(f"Telegram bildirim gönderilemedi: {e}")

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))

# =========================
# 🔹 SERVER
# =========================

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8001), Handler)
    print("Server started on port 8001")
    server.serve_forever()
