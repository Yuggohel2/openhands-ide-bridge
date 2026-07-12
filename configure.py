import os
import sys
import json
from pathlib import Path

def get_config_paths():
    home = Path.home()
    paths = {}
    
    if sys.platform == "win32":
        appdata = Path(os.environ.get("APPDATA", str(home / "AppData/Roaming")))
        paths["Claude Desktop"] = appdata / "Claude/claude_desktop_config.json"
        paths["Cline (VS Code)"] = appdata / "Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
        paths["Roo-Cline (VS Code)"] = appdata / "Code/User/globalStorage/roodev.roo-cline/settings/cline_mcp_settings.json"
    elif sys.platform == "darwin":  # macOS
        support = home / "Library/Application Support"
        paths["Claude Desktop"] = support / "Claude/claude_desktop_config.json"
        paths["Cline (VS Code)"] = support / "Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
        paths["Roo-Cline (VS Code)"] = support / "Code/User/globalStorage/roodev.roo-cline/settings/cline_mcp_settings.json"
    else:  # Linux
        config = home / ".config"
        paths["Claude Desktop"] = config / "Claude/claude_desktop_config.json"
        paths["Cline (VS Code)"] = config / "Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
        paths["Roo-Cline (VS Code)"] = config / "Code/User/globalStorage/roodev.roo-cline/settings/cline_mcp_settings.json"
        
    return paths

def main():
    print("🌉 OpenHands IDE Bridge - Auto Configuration Utility")
    print("====================================================")
    
    script_path = Path(__file__).parent.resolve() / "openhands_mcp.py"
    script_path_str = str(script_path).replace("\\", "/")
    
    mcp_config_block = {
        "command": "uv",
        "args": [
            "run",
            script_path_str
        ],
        "env": {
            "OPENHANDS_URL": "http://localhost:8000"
        }
    }
    
    paths = get_config_paths()
    found_any = False
    
    for name, path in paths.items():
        if path.exists():
            found_any = True
            print(f"\n[Found] {name} configuration file at:")
            print(f"        {path}")
            
            try:
                with open(path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                print(f"[Error] Failed to read/parse file: {e}")
                continue
                
            if "mcpServers" not in config:
                config["mcpServers"] = {}
                
            # Add or update openhands configuration
            config["mcpServers"]["openhands"] = mcp_config_block
            
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(config, f, indent=2)
                print(f"[Success] Successfully registered 'openhands' server in {name} config!")
            except Exception as e:
                print(f"[Error] Failed to write config back: {e}")
                
    if not found_any:
        print("\n[Notice] No active IDE MCP configuration files were detected automatically.")
        print("Please configure the MCP server manually in your IDE settings using this block:")
        print(json.dumps({"openhands": mcp_config_block}, indent=2))
        
if __name__ == "__main__":
    main()
