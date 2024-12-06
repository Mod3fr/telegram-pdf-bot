import os
import requests
from flask import Flask, request
from googletrans import Translator
from PyPDF2 import PdfReader

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}/"
translator = Translator()

@app.route("/")
def home():
    return "البوت يعمل بنجاح!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data and "document" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        file_id = data["message"]["document"]["file_id"]

        file_path = download_file(file_id)
        text = extract_pdf_text(file_path)
        translated_text = translator.translate(text, src='auto', dest='ar').text

        send_message(chat_id, translated_text)

    return "OK"

def download_file(file_id):
    file_info = requests.get(f"{API_URL}getFile?file_id={file_id}").json()
    file_path = file_info["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    response = requests.get(file_url)
    file_name = "uploaded.pdf"
    with open(file_name, "wb") as f:
        f.write(response.content)
    return file_name

def extract_pdf_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def send_message(chat_id, text):
    requests.post(f"{API_URL}sendMessage", data={"chat_id": chat_id, "text": text})

if __name__ == "__main__":
    app.run(debug=True)
