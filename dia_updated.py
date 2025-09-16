import requests
import time
import os

# ==========================
# CONFIGURATION
# ==========================
API_KEY = "d4b3963892a147b78627dcb3a42bcf3e"  # Replace with your API key
audio_file = r"C:\Users\Krishna\Desktop\Minor Project - 2\Data\audio3.mp3"

upload_url = "https://api.assemblyai.com/v2/upload"
transcribe_url = "https://api.assemblyai.com/v2/transcript"
headers = {"authorization": API_KEY}

# ==========================
# FUNCTIONS
# ==========================
def upload_file(path):
    """Uploads audio file to AssemblyAI and returns the file URL"""
    with open(path, "rb") as f:
        response = requests.post(upload_url, headers=headers, data=f)
    response.raise_for_status()
    return response.json()["upload_url"]

def request_transcription(audio_url):
    """Requests transcription with speaker diarization"""
    payload = {
        "audio_url": audio_url,
        "speaker_labels": True,  # Enable speaker diarization
        "iab_categories": False
    }
    response = requests.post(transcribe_url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["id"]

def wait_for_transcription(transcript_id):
    """Polls AssemblyAI until transcription is completed"""
    polling_endpoint = f"{transcribe_url}/{transcript_id}"
    while True:
        response = requests.get(polling_endpoint, headers=headers).json()
        status = response.get("status")
        if status == "completed":
            return response
        elif status == "error":
            raise RuntimeError(f"Transcription failed: {response.get('error')}")
        time.sleep(3)

def format_diarization(transcript_json):
    """Formats diarized transcription JSON into readable text"""
    words = transcript_json.get("words", [])
    if not words:
        return "[No diarization data found]"

    lines = []
    current_speaker = words[0].get("speaker", "Unknown")
    current_start = words[0].get("start", 0) / 1000
    current_end = words[0].get("end", 0) / 1000
    current_text = words[0].get("text", "")

    for w in words[1:]:
        speaker = w.get("speaker", "Unknown")
        start = w.get("start", 0) / 1000
        end = w.get("end", 0) / 1000
        text = w.get("text", "")

        if speaker == current_speaker:
            # same speaker → append word
            current_text += " " + text
            current_end = end
        else:
            # speaker changed → save previous line
            lines.append(f"[{current_start:.2f}s - {current_end:.2f}s] Speaker {current_speaker}: {current_text}")
            # start new speaker
            current_speaker = speaker
            current_start = start
            current_end = end
            current_text = text

    # append last segment
    lines.append(f"[{current_start:.2f}s - {current_end:.2f}s] Speaker {current_speaker}: {current_text}")
    return "\n".join(lines)

# ==========================
# MAIN SCRIPT
# ==========================
if __name__ == "__main__":
    print("⏳ Uploading audio file...")
    audio_url = upload_file(audio_file)
    print("✅ File uploaded.")

    print("🎙️ Requesting transcription with diarization...")
    transcript_id = request_transcription(audio_url)

    transcript_json = wait_for_transcription(transcript_id)
    print("✅ Transcription completed!\n")

    diarized_text = format_diarization(transcript_json)
    print(diarized_text)

    # Save to file
    out_path = os.path.join(os.path.dirname(audio_file), "diarized_transcription.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(diarized_text)
    print("💾 Saved at:", out_path)
