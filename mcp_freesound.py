from mcp.server.fastmcp import FastMCP
import json

import os
from dotenv import load_dotenv
import freesound

# Load .env file at module level (before any other code)
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("freesound")


api_key = os.getenv('FREESOUND_API_KEY', None)
if api_key is None:
    print("You need to set your API key as an environment variable")
    print("named FREESOUND_API_KEY")

freesound_client = freesound.FreesoundClient()
freesound_client.set_token(api_key)

@mcp.tool()
async def get_freesound_basic_info(sound_id: str) -> str:
    """ Get freesound sound info for id """
    sound = freesound_client.get_sound(int(sound_id))
    info_txt = "Getting sound:" +sound.name
    info_txt += "Url:"+ sound.url
    info_txt += "Description:"+sound.description
    info_txt += "Tags:" +` " ".join(sound.tags)
    return info_txt

def convert_to_wav(input_path: str) -> str:
    """Convert input audio file to .wav if not already in .wav format."""
    if input_path.lower().endswith('.wav'):
        return input_path
    output_path = os.path.splitext(input_path)[0] + ".wav"
    (
        ffmpeg.input(input_path)
        .output(output_path, acodec='pcm_s16le', ac=1, ar='44100')
        .overwrite_output()
        .run(quiet=True)
    )
    return output_path

if __name__ == "__main__":
    mcp.run(transport="stdio")
