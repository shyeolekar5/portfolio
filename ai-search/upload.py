from google import genai
from dotenv import load_dotenv
import requests
import os
import time

# 1. Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ Error: API Key not found. Check your .env file.")

client = genai.Client(api_key=api_key)

# --- DOWNLOAD PUBLIC PDF ---
pdf_url = "https://arxiv.org/pdf/1706.03762.pdf"
local_filename = "research_paper.pdf"

print(f"📥 Downloading 'Attention Is All You Need' from arXiv...")

# We use a User-Agent so arXiv knows we are a script but 'polite'
try:
    response = requests.get(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code == 200:
        with open(local_filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Download complete: Saved as {local_filename}")
    else:
        print(f"❌ Failed to download PDF (Status {response.status_code}).")
        exit()
except Exception as e:
    print(f"❌ Error downloading: {e}")
    exit()

# 2. Upload to Gemini
print(f"🚀 Uploading {local_filename} to Google Gemini...")

uploaded_files = []
try:
    f = client.files.upload(file=local_filename)
    uploaded_files.append(f)
    print(f"✅ Uploaded: {f.name}")
except Exception as e:
    print(f"❌ Error uploading: {e}")
    exit()

# 3. Wait for Processing
print(f"⏳ Waiting for file to process...")
while True:
    try:
        fresh_file = client.files.get(name=uploaded_files[0].name)
        
        if fresh_file.state.name == "ACTIVE":
            print("✅ File is ready for search!")
            break
        elif fresh_file.state.name == "FAILED":
            print(f"❌ Processing failed: {fresh_file.state.name}")
            break
    except Exception as e:
        print(f"Error checking status: {e}")
        
    print("... processing ...")
    time.sleep(5)

# 4. Save ID for the Server
with open("uploaded_file_names.txt", "w") as f:
    for file_obj in uploaded_files:
        f.write(file_obj.name + "\n")

print("\nSUCCESS! You can now push to GitHub and deploy.")