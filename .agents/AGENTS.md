# Agent Swarm Rules (IDE + OpenHands Sandbox Collaboration)

To ensure maximum efficiency and coordination when using this bridge in a multi-agent or IDE-integrated workflow, all agent loops must adhere to the following rules:

## 1. The Brain & Builder Division of Labor
- **Rule**: The host-level IDE assistant acts as **The Brain** (Architect/Planner). It handles project analysis, code design, file structures, and strategic steps.
- **Rule**: The sandboxed OpenHands agent acts as **The Builder** (Executioner). It is responsible for installing dependencies, compiling code, running tests, and executing bash processes.
- **Rule**: Whenever the IDE assistant needs to execute terminal commands, run test suites, or perform complex multi-file compilation, it must delegate these actions to OpenHands via the MCP tools (e.g., `execute_bash` or `run_task`) rather than running commands directly on the host system.

## 2. Leverage Agent Swarms (Parallel Execution) When Feasible
- **Rule**: Whenever tasks are decoupled and have no linear dependencies (such as parallel unit testing, parallel security audits, or independent feature development on separate branches), the IDE assistant should spawn parallel agent threads or concurrent execution loops rather than running everything sequentially.
- **Rule**: The proxy server supports this natively by isolating concurrent requests using unique transaction UUIDs (`llm_request_<uuid>.json` and `llm_response_<uuid>.json`).

## 3. Sandboxed Command Safety
- **Rule**: When executing terminal commands inside the OpenHands sandbox, always run background processes or long-running development servers with non-blocking execution commands (e.g., using `nohup` or `&` in the background) to prevent the MCP connection socket from hanging.
- **Rule**: Standard commands must enforce a strict timeout to ensure the execution loop remains responsive and fails gracefully on hangs.
