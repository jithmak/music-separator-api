import subprocess
import sys
import os
from pathlib import Path

def separate_music(input_file):
    """
    Runs the Demucs stem separation command on a given audio file.
    
    Returns:
        Path: The path to the *output folder* containing the stems,
              or None if separation failed.
    """
    
    # --- 1. Validate Input ---
    # Convert input_file to a Path object for easier handling
    input_path = Path(input_file)

    # Check if the file exists
    if not input_path.exists():
        print(f"Error: File not found at '{input_file}'")
        return None
        
    # Check if the file is actually a file
    if not input_path.is_file():
        print(f"Error: Path '{input_file}' is a directory, not a file.")
        return None

    # --- 2. Define Command & Output ---
    
    # We'll create a dedicated output directory
    output_dir = Path("separated_output")
    
    # This is the base file name without the extension (e.g., "my_song")
    file_stem = input_path.stem

    # Define the command we want to run.
    # This is identical to typing:
    # `demucs -o "separated_output" "my_song.mp3"`
    # in the terminal.
    command = [
        "demucs",
        "-o", str(output_dir),  # "-o" specifies the output directory
        str(input_path)         # The last argument is the file to process
    ]

    # --- 3. Run the Command ---
    print(f"Starting separation for: {input_path.name}...")
    
    try:
        # `subprocess.run()` executes the command.
        # `check=True` means it will raise an error if demucs fails.
        # `capture_output=True` and `text=True` are good practices
        # to capture an logs or errors from the command.
        
        # We store the result to check it
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        print("Separation complete!")
        
        # --- This is the new/changed part ---
        
        # Demucs creates a folder structure like:
        # `separated_output/<model_name>/<file_stem>/`
        # We need to find this folder.
        
        # We can find the model name from stdout, but it's complex.
        # A simpler (but less robust) way is to find the
        # first folder inside `separated_output`.
        # Note: Demucs' output format can change.
        
        # Let's parse the stdout to find the real model name
        model_name = "htdemucs" # Default
        for line in result.stdout.splitlines():
            # This is a bit of a hack, but works for demucs
            if "Selected model" in line or "default model" in line:
                # Find the model name, which is often in quotes or at the end
                parts = line.split(" ")
                if len(parts) > 0:
                    model_name = parts[-1].strip("'.")
                break
        
        # This is the path we will return
        final_output_path = output_dir / model_name / file_stem
        
        if not final_output_path.exists():
            # Fallback: Just return the base output dir
            print(f"Warning: Could not find expected path '{final_output_path}'. Returning base path.")
            return output_dir

        print(f"Find your stems in: {final_output_path.resolve()}")
        
        # Return the *path* to the output folder
        return final_output_path
        
    except subprocess.CalledProcessError as e:
        # This block runs if Demucs throws an error
        print(f"Error during separation:")
        print("--- STDOUT ---")
        print(e.stdout)
        print("--- STDERR ---")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print("Error: 'demucs' command not found.")
        print("Please ensure demucs is installed and your virtual environment is active.")
        return None

if __name__ == "__main__":
    # This block runs when you execute `python run_separation.py`
    
    # Check if the user provided a file name argument
    if len(sys.argv) < 2:
        print("Usage: python run_separation.py <path_to_your_audio_file>")
    else:
        # The first argument (sys.argv[0]) is the script name.
        # The second (sys.argv[1]) is the file we want.
        file_to_.process = sys.argv[1]
        
        # Call the function
        output_path = separate_music(file_to_process)
        
        if output_path:
            print(f"Script finished. Output at: {output_path}")
        else:
            print("Script finished with errors.")

