from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import logging
import time

# 1. Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2. Load Env
load_dotenv()

app = FastAPI()

# 3. Security: CORS
# Restricts access to your specific Google Site
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://740750457-atari-embeds.googleusercontent.com", 
        "https://sites.google.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Client Setup
api_key = os.getenv("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

# --- THE SELF-HEALING UPLOAD SYSTEM ---
# This variable acts as the server's memory of the file location
CACHED_FILE_URI = None

def get_or_upload_file():
    """
    Ensures the PDF is uploaded to Gemini and returns the URI.
    If the file is expired or missing, it uploads it automatically.
    """
    global CACHED_FILE_URI
    
    # Check if we already have a valid URI in memory
    if CACHED_FILE_URI:
        try:
            # Extract ID and check status with Google
            file_name = CACHED_FILE_URI.split("/")[-1] 
            file_obj = client.files.get(name=file_name)
            if file_obj.state.name == "ACTIVE":
                return CACHED_FILE_URI
        except Exception:
            logger.warning("Cached file expired. Re-uploading...")

    # If we get here, the file is missing/expired. Let's upload it.
    logger.info("Uploading PDF to Gemini...")
    
    if not os.path.exists("research_paper.pdf"):
        logger.error("research_paper.pdf not found on server!")
        return None

    try:
        # Upload the file
        f_obj = client.files.upload(file="research_paper.pdf")
        
        # Wait for Google to process it
        while f_obj.state.name == "PROCESSING":
            time.sleep(1)
            f_obj = client.files.get(name=f_obj.name)
            
        if f_obj.state.name != "ACTIVE":
            logger.error(f"File processing failed: {f_obj.state.name}")
            return None
            
        # Success! Cache the new URI
        CACHED_FILE_URI = f_obj.uri
        logger.info(f"File ready: {CACHED_FILE_URI}")
        return CACHED_FILE_URI
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return None

# Run once on startup to "warm up" the server
get_or_upload_file()

# 5. Define Input Model
class SearchQuery(BaseModel):
    question: str

@app.post("/search")
def search_documents(query: SearchQuery):
    if not client:
        raise HTTPException(status_code=500, detail="Server Configuration Error")

    # Get the valid file URI (auto-uploads if needed)
    file_uri = get_or_upload_file()
    
    if not file_uri:
         raise HTTPException(status_code=503, detail="Document unavailable. Check server logs.")

    try:
        system_instruction = (
            "You are a strict research assistant. Use the provided documents to answer the user's question. "
            "If the answer is not found in the documents, state that you do not know."
        )
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=[
                system_instruction,
                types.Part.from_uri(file_uri=file_uri, mime_type="application/pdf"),
                query.question
            ]
        )
        return {"answer": response.text}

    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error.")