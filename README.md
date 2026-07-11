# OpenHands IDE Bridge 🌉

A lightweight, zero-configuration local proxy server that allows **OpenHands** to run on your system's native/IDE-licensed LLMs (e.g., Gemini, Claude, or GPT) instead of requiring direct LLM API keys.

---

## How It Works

1. **Proxy HTTP Server:** Runs on your host machine (default port `9999`) and intercepts standard OpenAI-compatible `/chat/completions` HTTP requests sent by OpenHands.
2. **File-Based Communication:** For each request, the proxy creates a temporary JSON file (`llm_request_<id>.json`) in your local `.openhands/` directory.
3. **IDE Processing:** Your active IDE coding assistant (which has native access to LLMs) detects the file, calls the LLM, writes the output to `llm_response_<id>.json`, and cleans up.
4. **Transparent Interface:** The proxy reads the response and returns it to OpenHands as a standard HTTP response.

This means **no code modifications** are required inside OpenHands. It behaves exactly as if it was calling a direct OpenAI API, but uses your local/IDE LLM for free.

---

## Installation & Running

### 1. Start the Proxy Server
Run the proxy server on your host machine:

```bash
# Clone the repository
git clone https://github.com/Yuggohel2/openhands-ide-bridge.git
cd openhands-ide-bridge

# Run the proxy (it will start on port 9999)
python llm_proxy.py
```

### 2. Configure OpenHands
Start OpenHands by pointing its LLM settings to the proxy server:

#### A. If Running OpenHands in Docker (Recommended)
Set the environment variables when executing the `docker run` command. Note that inside Docker, `host.docker.internal` is used to refer to your host computer:

```bash
docker run -it \
  -e LLM_BASE_URL="http://host.docker.internal:9999/v1" \
  -e LLM_MODEL="openai/custom-model" \
  -e LLM_API_KEY="not-needed" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  ghcr.io/all-in-ai/openhands:0.9
```

#### B. If Using the OpenHands Web UI Settings
In the OpenHands Web UI settings panel:
* **Language Model Provider:** `OpenAI (Compatible)`
* **Model Name:** `custom-model`
* **API Base URL:** `http://host.docker.internal:9999/v1`
* **API Key:** `dummy`

---

## Port Customization
By default, the proxy runs on port `9999`. If this port is occupied, it will automatically attempt to bind to the next free port. 

If you want to force a custom port, set the `LLM_PROXY_PORT` environment variable before running:
```bash
# Windows (PowerShell)
$env:LLM_PROXY_PORT=8888
python llm_proxy.py

# macOS / Linux / Git Bash
LLM_PROXY_PORT=8888 python llm_proxy.py
```

---

## License
MIT License. See [LICENSE](LICENSE) for details.
