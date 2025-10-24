import subprocess
import uvicorn
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException

# --- 1. Import our separation function ---
# We can now import this function directly from our other .py file
# This is a much cleaner way to organize our code.
try:
    from run_separation import separate_music
except ImportError:
    print("Error: Could not import 'separate_music' from 'run_separation.py'.")
    print("Make sure 'run_separation.py' is in the same directory.")
    exit()

# --- 2. Initialize our FastAPI app ---
app = FastAPI()

# --- 3. Create helper directories ---
# Create directories to store uploaded and processed files
# The .mkdir(exist_ok=True) command is a safe way to create
# a directory, as it won't raise an error if it already exists.
Path("uploads").mkdir(exist_ok=True)
Path("separated_output").mkdir(exist_ok=True)


# --- 4. Define our API endpoints ---

@app.get("/")
def read_root():
    """
    A simple "hello world" endpoint to confirm the server is running.
    """
    return {"message": "Welcome to the AI Music Separator API!"}


@app.post("/separate/")
async def separate_audio_endpoint(file: UploadFile = File(...)):
    """
    This is the main endpoint that handles file uploads and separation.
    'async def' means it's an asynchronous endpoint, which is
    better for handling uploads and long-running tasks.
    """
    
    # --- 5. Save the uploaded file ---
    # We save the uploaded file to our 'uploads' directory
    # so that our Demucs script can read it from the disk.
    
    # We use a Path object to safely construct the file path
    upload_path = Path("uploads") / file.filename
    
    try:
        # We use shutil.copyfileobj to efficiently save the file.
        # 'file.file' is the file-like object provided by FastAPI.
        with upload_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        # If saving fails, we return an error.
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    finally:
        # It's important to close the file.
        file.file.close()

    print(f"File saved to: {upload_path}")

    # --- 6. Run the separation ---
    # Now we call our imported function on the file we just saved.
    # This will run the `demucs` command and block until it's done.
    # (In a production app, we'd make this a background task,
    # but for learning, this is perfect.)
    
    try:
        output_folder_path = separate_music(upload_path)
        
        if output_folder_path is None:
            raise HTTPException(status_code=500, detail="Separation failed. Check server logs.")

    except subprocess.CalledProcessError as e:
        # If the 'demucs' command fails, we return a detailed error
        raise HTTPException(status_code=500, 
                            detail={"error": "Demucs process failed", 
                                    "stdout": e.stdout, 
                                    "stderr": e.stderr})
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
        
    print(f"Separation complete. Stems in: {output_folder_path}")

    # --- 7. Return the result ---
    # For now, we just return a success message and the path to the
    # folder containing the stems. In a future step, we could
    # zip these files and send them back.
    return {
        "message": "Separation complete!",
        "output_path": str(output_folder_path)
    }

# --- 8. Add the "main" block to run the server ---
if __name__ == "__main__":
    """
    This block allows us to run the server directly with:
    `python main.py`
    
    However, for development, it's better to use:
    `uvicorn main:app --reload`
    """
    uvicorn.run(app, host="127.0.0.1", port=8000)
