import subprocess
import os
import sys

# --- Configuration ---
# 1. PASTE YOUR FULL YOUTUBE URL HERE
VIDEO_URL = "https://www.youtube.com/watch?v=NRntuOJu4ok"  # <-- REPLACE THIS

# 2. Set your timestamps
START_TIME = "253.9"
END_TIME = "337.4"

# 3. Set your output filenames
AUDIO_FILENAME = "temp_audio_clip.mp3"
TRANSCRIPT_FILENAME = "temp_audio_clip.txt"

# 4. Set your Whisper model (e.g., tiny, base, small, medium, large)
# 'base.en' is a good balance of speed and accuracy for English.
WHISPER_MODEL = "base.en"
# -------------------------

def run_command(command):
    """Runs a system command and prints its output."""
    print(f"\n--- Running Command: {' '.join(command)} ---")
    try:
        # We use shell=True here for simplicity with complex commands,
        # but be cautious with untrusted inputs.
        # For this script, it helps find ffmpeg/yt-dlp in the system PATH.
        subprocess.run(
            " ".join(command), 
            check=True, 
            shell=True, 
            stdout=sys.stdout, 
            stderr=sys.stderr
        )
        print(f"--- Command Succeeded ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"--- ERROR: Command Failed ---")
        print(f"Return Code: {e.returncode}")
        print(f"Output: {e.output}")
        return False
    except FileNotFoundError as e:
        print(f"--- ERROR: Command not found ---")
        print(f"'{e.filename}' not found. Is it installed and in your system's PATH?")
        print("This script requires 'yt-dlp', 'ffmpeg', and 'whisper' to be installed.")
        return False

def main():
    if "REPLACE THIS" in VIDEO_URL:
        print("=" * 60)
        print("ERROR: Please update the 'VIDEO_URL' variable in the script")
        print("with your actual YouTube video link.")
        print("=" * 60)
        return

    # --- Step 1: Download and Clip Audio using yt-dlp ---
    # This command tells yt-dlp to:
    # -x : Extract audio
    # --audio-format mp3 : Convert it to MP3
    # -o : Set the output filename
    # --external-downloader ffmpeg : Use ffmpeg for post-processing
    # --external-downloader-args : Pass the -ss (start) and -to (end) commands to ffmpeg
    
    yt_dlp_command = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "-o", f'"{AUDIO_FILENAME}"',
        "--external-downloader", "ffmpeg",
        "--external-downloader-args", f'"ffmpeg_i:-ss {START_TIME} -to {END_TIME}"',
        f'"{VIDEO_URL}"'
    ]
    
    # if not run_command(yt_dlp_command):
    #     print("\nFailed to download or clip audio. Exiting.")
    #     return

    if not os.path.exists(AUDIO_FILENAME):
        print(f"\nError: Audio file '{AUDIO_FILENAME}' was not created. Check yt-dlp/ffmpeg output.")
        return

    print(f"\nSuccessfully created audio clip: {AUDIO_FILENAME}")

    # --- Step 2: Transcribe the Audio Clip using Whisper ---
    # This command tells whisper to:
    # - Transcribe the specified audio file
    # --model : Use the 'base.en' model
    # --output_format txt : Save the transcript as a simple .txt file
    
    whisper_command = [
        "faster-whisper-xxl",
        f'"{AUDIO_FILENAME}"',
        "--model", WHISPER_MODEL,
        "--output_format", "txt",
        "--output_dir", ".",
        "--language", "en"
    ]

    if not run_command(whisper_command):
        print("\nFailed to transcribe audio. Exiting.")
        return

    if not os.path.exists(TRANSCRIPT_FILENAME):
        print(f"\nError: Transcript file '{TRANSCRIPT_FILENAME}' was not created. Check whisper output.")
        return
        
    print(f"\nSuccessfully created transcript: {TRANSCRIPT_FILENAME}")

    # --- Step 3: Print the Transcript ---
    try:
        with open(TRANSCRIPT_FILENAME, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        print("\n" + "=" * 60)
        print(f" TRANSCRIPT ({START_TIME}s - {END_TIME}s) ")
        print("=" * 60)
        print(transcript)
        print("=" * 60)

    except FileNotFoundError:
        print(f"\nError: Could not find transcript file '{TRANSCRIPT_FILENAME}' to read.")
    except Exception as e:
        print(f"\nAn error occurred while reading the transcript file: {e}")

    # --- Step 4: Clean up temporary files ---
    try:
        print(f"\nCleaning up files...")
        if os.path.exists(AUDIO_FILENAME):
            os.remove(AUDIO_FILENAME)
            print(f"Removed: {AUDIO_FILENAME}")
        if os.path.exists(TRANSCRIPT_FILENAME):
            os.remove(TRANSCRIPT_FILENAME)
            print(f"Removed: {TRANSCRIPT_FILENAME}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()
