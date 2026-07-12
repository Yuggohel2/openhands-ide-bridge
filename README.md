# OpenHands IDE Bridge 🌉

> **Are you tired of getting your API keys exhausted by OpenHands?**  
> Meet the solution that routes OpenHands calls directly to your **IDE's native LLM**—no extra API keys, no usage limits, and completely free.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Yuggohel2/openhands-ide-bridge/pulls)

---

## 🛑 The Problem
Running agentic systems like **OpenHands** locally is incredibly powerful, but it can quickly consume thousands of tokens, exhausting your paid LLM API keys (OpenAI, Anthropic, etc.) in a matter of minutes. At the same time, you already have an AI-powered IDE or chat assistant with active, high-quality models (Gemini, Claude, GPT-4) running right on your desktop.

## 💡 The Solution
The **OpenHands IDE Bridge** is a lightweight, zero-configuration local proxy server. It intercepts standard OpenAI-compatible `/chat/completions` API calls sent by OpenHands and translates them into local file exchanges (`llm_request_*.json` / `llm_response_*.json`) inside the standard `~/.openhands/` directory.

Any active IDE assistant or local agent running on your host machine can then intercept these requests, solve them using its native LLM access, and write back the response—giving OpenHands full agentic capabilities **without spending a single cent on raw API keys**.

---

## ⚡ Save Up to 80% More Tokens with Hercules MCP!
If you want to optimize your token efficiency even further when running local agents, check out the parent project: **[Hercules MCP](https://github.com/Yuggohel2/hercules-mcp)**.

Hercules MCP integrates OpenHands with a **Code Review Graph** database and token-saving rules:
* **Graph-First Analysis:** Avoids listing full directories or scanning entire files. It queries a localized graph structure to locate exact dependencies.
* **Smart Context Archiving:** Automatically packages and archives task logs to prevent context bloat.
* **Token Savings:** Saves up to **75% to 80% of your LLM tokens** per session by restricting context retrieval to narrow, relevant scopes.

Check out the [Hercules MCP Repository](https://github.com/Yuggohel2/hercules-mcp) to supercharge your local agent setup!

---

## 🔌 Supported IDEs & Extensions

This bridge is compatible with any editor, environment, or extension that can hook into the standard file-based polling protocol in your `~/.openhands` folder. Examples include:

* **VS Code / Cursor / Windsurf** with custom local agent loops or scripts.
* **Antigravity / Gemini Code Assist** environments configured to watch local directories for proxy requests.
* **Continue.dev** or other open-source IDE extensions when integrated with local interceptors.
* **Custom Desktop Agents** running alongside your development workspace.

*Any IDE or plugin that can read `llm_request_<id>.json`, call its native model (which is already authorized, e.g., to write files, edit code, and execute terminal commands), and output `llm_response_<id>.json` can drive the OpenHands sandbox seamlessly.*

---

## 🤖 Cooperative Agent Swarms (The Brain & The Builder)

By running the included **MCP (Model Context Protocol) Server**, you unlock a powerful collaborative workflow where your IDE assistant and OpenHands work together:

1. **The Brain (IDE LLM):** Acts as the Architect. It plans features, designs codebases, and manages task checklists.
2. **The Builder (OpenHands Sandbox):** Acts as the Operator. When the Brain needs to run bash commands, execute unit tests, or compile code, it delegates the work to OpenHands via MCP tools (`execute_bash`, `run_task`, `create_conversation`).
3. **Concurrency-Safe Swarms:** Because the proxy isolates concurrent requests using unique UUIDs, you can have your IDE assistant spawn multiple OpenHands tasks or running loops in parallel.

This division of labor keeps your host system safe while letting the AI execute code in a secure sandbox. The rules for establishing this cooperation are defined in [`.agents/AGENTS.md`](.agents/AGENTS.md).

---

## 🚀 Quick Start

### 1. Run the Proxy Server
Run the proxy server on your host machine (where your IDE is running):

```bash
# Clone the repository
git clone https://github.com/Yuggohel2/openhands-ide-bridge.git
cd openhands-ide-bridge

# Start the proxy (runs on port 9999 by default)
python llm_proxy.py
```

### 2. Configure OpenHands
Launch OpenHands and tell it to send its API requests to the proxy:

#### A. If Running OpenHands in Docker (Recommended)
Add these environment variables when starting your container. Inside Docker, `host.docker.internal` allows the container to talk to the proxy running on your host:

```bash
docker run -it \
  -e LLM_BASE_URL="http://host.docker.internal:9999/v1" \
  -e LLM_MODEL="openai/native-ide-model" \
  -e LLM_API_KEY="not-needed" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  ghcr.io/all-in-ai/openhands:0.9
```

#### B. If Configuring via the OpenHands Web UI
Simply enter the following details in the settings panel:
* **Language Model Provider:** `OpenAI (Compatible)`
* **Model Name:** `native-ide-model`
* **API Base URL:** `http://host.docker.internal:9999/v1`
* **API Key:** `dummy`

### 3. Expose OpenHands to your IDE (Optional MCP Server Setup)
To allow your IDE assistant to control OpenHands, add the MCP server configuration to your IDE settings (e.g. `mcp_config.json`):

```json
"openhands": {
  "command": "uv",
  "args": [
    "run",
    "/absolute/path/to/openhands_mcp.py"
  ],
  "env": {
    "OPENHANDS_URL": "http://localhost:8000"
  }
}
```

Make sure your OpenHands container is running, then your IDE assistant will instantly gain access to the OpenHands tool suite!

---

## ⚙️ Advanced Customization

### Port Binding
If port `9999` is occupied, the proxy will automatically bind to the next free port (e.g. `9998`, `9997`). 

To override this and force a specific port, set the `LLM_PROXY_PORT` environment variable:
```bash
# Windows (PowerShell)
$env:LLM_PROXY_PORT=8888
python llm_proxy.py

# macOS / Linux / Git Bash
LLM_PROXY_PORT=8888 python llm_proxy.py
```

---

## 📄 License
Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
