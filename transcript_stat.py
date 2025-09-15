import requests
import time
import os

API_KEY = "d4b3963892a147b78627dcb3a42bcf3e"

headers = {"authorization": API_KEY}
upload_url = "https://api.assemblyai.com/v2/upload"
transcribe_url = "https://api.assemblyai.com/v2/transcript"

audio_file = r"C:\Users\Krishna\Desktop\Minor Project - 2\Data\audio2.mp3"

# Upload file
def upload_file(path):
    with open(path, "rb") as f:
        response = requests.post(upload_url, headers=headers, data=f)
    return response.json()["upload_url"]

# Request transcription
def request_transcription(audio_url):
    json = {"audio_url": audio_url}
    response = requests.post(transcribe_url, headers=headers, json=json)
    return response.json()["id"]

# Poll until completed
def wait_for_transcription(transcript_id):
    polling_endpoint = f"{transcribe_url}/{transcript_id}"
    while True:
        response = requests.get(polling_endpoint, headers=headers).json()
        if response["status"] == "completed":
            return response["text"]
        elif response["status"] == "error":
            raise RuntimeError(response["error"])
        time.sleep(3)

if __name__ == "__main__":
    print("⏳ Uploading...")
    audio_url = upload_file(audio_file)
    print("✅ File uploaded.")
    transcript_id = request_transcription(audio_url)
    print("🎙️ Transcribing...")
    text = wait_for_transcription(transcript_id)
    print("✅ Done!\n")
    print(text)

    # Save to file
    out_path = os.path.join(os.path.dirname(audio_file), "transcription.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("💾 Saved at:", out_path)
