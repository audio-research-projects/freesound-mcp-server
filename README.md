# Freesound MCP server

Based on the freesound API on https://github.com/MTG/freesound-python

DISCLAIMER: be careful about prompt-injection, there is no input sanitization or validation

## MCP config
### Dependencies

    pip install poetry
    poetry install --no-root # package-mode false


### Create .env file with your Freesound API KEY

    FREESOUND_API_KEY=

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