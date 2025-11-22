from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

# Load environment variables 
load_dotenv()

app = FastAPI()

# Allow CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Client
api_key = os.getenv("GEMINI_API_KEY")
client = None
if api_key:
    client = genai.Client(api_key=api_key)

# Load File IDs on startup
file_ids = []
try:
    if os.path.exists("uploaded_file_names.txt"):
        with open("uploaded_file_names.txt", "r") as f:
            file_ids = [l.strip() for l in f.readlines() if l.strip()]
        print(f"Loaded {len(file_ids)} file IDs.")
    else:
        print("Warning: uploaded_file_names.txt not found.")
except Exception as e:
    print(f"Error loading files: {e}")

class SearchQuery(BaseModel):
    question: str

@app.post("/search")
def search_documents(query: SearchQuery):
    if not client:
        raise HTTPException(status_code=500, detail="Server Error: API Key not configured.")
    
    if not file_ids:
         raise HTTPException(status_code=500, detail="Server Error: No file IDs found. Please run upload.py locally and push the text file.")

    # 1. Resolve IDs to URIs (Lazy Check)
    active_uris = []
    for fid in file_ids:
        try:
            f_obj = client.files.get(name=fid)
            active_uris.append(f_obj.uri)
        except:
            continue # Skip expired files
            
    if not active_uris:
        raise HTTPException(status_code=500, detail="No active documents found. They may have expired (48h limit). Re-run upload.py.")

    # 2. Generate Answer
    try:
        file_parts = [types.Part.from_uri(file_uri=u, mime_type="application/pdf") for u in active_uris]

        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=[
                "You are a helpful assistant. Answer strictly based on the provided documents.",
                *file_parts,
                query.question
            ]
        )
        return {"answer": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))