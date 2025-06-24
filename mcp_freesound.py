from mcp.server.fastmcp import FastMCP
import json

import os
from dotenv import load_dotenv
import freesound
from MIRState import *
from typing import Any

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
    info_txt += "Tags:" + " ".join(sound.tags)
    return info_txt

def format_sound(sound: dict[str, Any]) -> str:
    """Format a sound instance into a readable string."""
    return f"""
        id: {sound.id}
        Name: {sound.name}
        Username: {sound.username}
       """

@mcp.tool()
async def get_freesound_search_by_content(sound_content_description: str) -> str:
        """ search a sound in freesound using a content descritpion"""
        results = freesound_client.text_search(query=sound_content_description,fields="id,name,username")
        info_txt = "Number of results:"+str(results.count)
        sounds = [format_sound(sound) for sound in results]
        return info_txt+"\n---\n".join(sounds)

@mcp.tool()
async def get_freesound_search_by_mir_features(sound_mir_features_description: str) -> str:
        """
            Search for Freesound audio clips based on MIR (Music Information Retrieval) feature filters.

            The function expects a string representing a dictionary of MIR descriptors.
            Each key should be one of the supported MIR features, and values must be numbers.

            Supported descriptors include:
                - "duration": max duration in seconds
                - "bpm": beats per minute
                - "hfc.mean": high-frequency content mean
                - "spectral_complexity.mean"
                - "spectral_centroid.mean" 
                - "pitch.mean"
                - "pitch_centroid.mean"
                - "pitch_salience.mean"
                - "inharmonicity.mean"
                - "dissonance.mean"
                - "chords_strength.mean"

            All the .mean values are in 0..1 float range.     

            Example usage (stringified dictionary):
                get_freesound_search_by_mir_features("{'duration': 30, 'dissonance.mean': 0.7}")

            This will return a summary of matched Freesound results.
        """
        results = freesound_client.text_search(query=sound_mir_features_description,fields="id,name,username")
        info_txt = "Number of results:"+str(results.count)
        sounds = [format_sound(sound) for sound in results]
        return info_txt+"\n---\n".join(sounds)
        
        # mir_state = MIRState()

        # mir_state.set_desc("")
#     mir_state

#     # desc_filter = "lowlevel.pitch.var:[* TO 20]" 
#     # desc_target = "lowlevel.pitch_salience.mean:1.0 lowlevel.pitch.mean:440"
#     desc_filter = ""
#     desc_target = ""
#     for desc,value in mir_state.iteritems():
#         if "TO" in str(value):
#             print("Filter by: "+desc)
#             desc_filter = desc+":["+value+"]"
#         elif desc=="tags" or desc=="content":
#             print("Tags/content not yet supported")
#         else:
#             print("Target: "+desc)
#             desc_target += desc+":"+str(value) + " "
    
#     print("Filter: "+desc_filter)
#     print("Target: "+desc_target)
#     # desc_filter = "lowlevel.pitch.var:[* TO 20]" 
#     # desc_target = "lowlevel.pitch_salience.mean:1.0 lowlevel.pitch.mean:440"

#     results_pager = freesound_client.content_based_search(
#                 descriptors_filter=desc_filter,
#                 target=desc_target,
#                 fields="id,name,username"
#             )
#     info_txt = "Num results:", results_pager.count
#     sounds = [format_sound(sound) for sound in results_pager]
#     return info_txt+"\n---\n".join(sounds)

#     # new_list = list()
#     # for sound in results_pager:
#     #     print("\t-", sound.name, "by", sound.username)
#     #     new_list.append(sound)
#     # return new_list 

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
