# Freesound MCP server

Based on the freesound API on https://github.com/MTG/freesound-python

DISCLAIMER: be careful about prompt-injection, there is no input sanitization or validation

## Demo

Check a demostration here
https://youtu.be/YVC5r43rQIg

First improve the prompt, LLMs + MCP to iterate the search for sounds in the sound database (Freesound.org). Then, generate code to render sound in Supercollider and create visuals for the browser:

    0:00 - Assistant message in Calliope
    0:09 - Initial prompt for the sound work (textual description)
    6:25 - Final prompt for the sound work (textual description)
    6:32 - Searching for samples using prompts and MIR functions    
    9:00 - Building the code in Supercollider to render sound
    10:50 - Creating visuals to accompany the work
    13:04 - Iteration to change the violin sounds for others
    13:58 - Final Supercollider script with sample comparison
    14:15 - Setting visual preferences
    14:25 - Playing the work: sound + visuals (3 minutes long)

## MCP config
### Dependencies

    pip install poetry
    poetry install --no-root # package-mode false


### Create .env file with your Freesound API KEY

    FREESOUND_API_KEY=

Request one here https://freesound.org/home/login/?next=/apiv2/apply

### Edit your llm config file like this

For exmple ~/Library/Application\ Support/Claude/claude_desktop_config.json

    {
    "mcpServers": {
        "freesound": {
        "command": "uv",
        "args": [
            "--directory",
            "$YOUR-PATH/freesound-mcp-server",
            "run",
            "mcp_freesound.py"
        ]
        },
    }

## Run Supercollider server like this

(
s.waitForBoot {
    // SynthDef that plays a buffer
    SynthDef(\playSample, {
        arg buf;
        var sig;
        sig = PlayBuf.ar(1, buf, doneAction: 2);
        Out.ar(0, sig);
    }).add;

    // Declare a dictionary to keep track of loaded buffers
    ~buffers = IdentityDictionary.new;

    // OSC handler
    OSCdef(\play_sound, { |msg|
        var path, buf;

        path = msg[1];
        postln("Received /play_sound for: " ++ path);

        // Avoid reloading if already in memory
        if (~buffers[path].notNil) {
            Synth(\playSample, [\buf, ~buffers[path].bufnum]);
        } {
            // Load and play buffer
            Buffer.read(s, path, action: { |b|
                ~buffers[path] = b;
                Synth(\playSample, [\buf, b.bufnum]);
            });
        };
    }, '/play_sound');

    postln("OSC handler for /play_sound is ready.");
};
)
