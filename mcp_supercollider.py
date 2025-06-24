from mcp.server.fastmcp import FastMCP
import json
import os
from dotenv import load_dotenv
import freesound
from pythonosc import udp_client
import asyncio
import subprocess

# Load .env file at module level (before any other code)
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("supercollider")

# Initialize Freesound client
api_key = os.environ.get("FREESOUND_API_KEY")
if not api_key:
    raise ValueError("FREESOUND_API_KEY environment variable not set. You can get a key from https://freesound.org/home/app_new/")

freesound_client = freesound.FreesoundClient()
freesound_client.set_token(api_key, "token")

# Initialize OSC client for SuperCollider
sc_client = udp_client.SimpleUDPClient("127.0.0.1", 57120)

@mcp.tool()
async def download_and_play(sound_id: str) -> str:
    """
    Downloads a sound from Freesound by its ID, converts it to WAV,
    and sends an OSC message to SuperCollider to play it.
    Returns info_txt plus a JSON dump of a list with sound info.
    """
    try:
        sound = freesound_client.get_sound(int(sound_id))
        info_txt = f"Getting sound: {sound.name}\n"
        info_txt += f"Url: {sound.url}\n"

        download_dir = "sounds"
        os.makedirs(download_dir, exist_ok=True)
        
        # Use a sanitized version of the sound name for the filename
        sanitized_name = "".join(c for c in sound.name if c.isalnum() or c in (' ', '.', '_')).rstrip()
        filename_stem = f"{sound.id}_{sanitized_name}"
        preview_filename = f"{filename_stem}.mp3"
        download_path = os.path.join(download_dir, preview_filename)

        # Retrieve the high-quality MP3 preview in a separate thread
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, sound.retrieve_preview, download_dir, preview_filename
        )

        info_txt += f"Downloaded preview to {download_path}\n"
        
        wav_path = convert_to_wav(download_path)
        info_txt += f"Converted to {wav_path}\n"
        
        # Send OSC message to SuperCollider
        sc_client.send_message("/play_sound", os.path.abspath(wav_path))
        info_txt += "Sent OSC message to SuperCollider to play the sound.\n"

        # Build new_list with relevant info
        new_list = [{
            "name": sound.name,
            "url": sound.url,
            "local_path": os.path.abspath(download_path),
            "wav_path": os.path.abspath(wav_path)
        }]

        return info_txt + "\n" + json.dumps(new_list, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"An error occurred: {e}"

def convert_to_wav(input_path: str) -> str:
    """Convert input audio file to .wav if not already in .wav format, using ffmpeg CLI."""
    if input_path.lower().endswith('.wav'):
        return input_path
    output_path = os.path.splitext(input_path)[0] + ".wav"
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path, "-acodec", "pcm_s16le", "-ac", "1", "-ar", "44100", output_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg conversion failed: {e.stderr.decode()}")
    return output_path

@mcp.tool()
async def get_freesound_descriptor(sound_id: str, descriptor: str) -> str:
    """
    Get a specific analysis descriptor from a Freesound sound by its id and descriptor path.
    Example: get_freesound_descriptor('12345', 'lowlevel.spectral_centroid')
    See all possible descriptors at https://freesound.org/docs/api/analysis_docs.html
    """
    try:
        # Request all analysis data for the sound
        sound = freesound_client.get_sound(int(sound_id), fields="id,name,analysis", normalized=1)
        analysis = sound.get_analysis()
        # Traverse the descriptor path (e.g., 'lowlevel.spectral_centroid')
        parts = descriptor.split('.')
        obj = analysis
        for part in parts:
            obj = getattr(obj, part)
        # If the final object has as_dict(), use it
        if hasattr(obj, 'as_dict'):
            return str(obj.as_dict())
        # Otherwise, just return its string representation
        return str(obj)
    except Exception as e:
        return f"Error retrieving descriptor '{descriptor}' for sound {sound_id}: {e}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
