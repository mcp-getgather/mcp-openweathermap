# api-weather-mcp
Basic HTTP MCP server for a weather app using a weather API


A containerized version of the weather mcp at https://modelcontextprotocol.io/quickstart/server

## Quickstart

### Connecting Your MCP Client to a Deployed Instance

For convenience, we have deployed the container using fly.io at https://getgather-weather.fly.dev/mcp. If you so desire, you can connect your MCP client directly to this instance. For example, in Cursor/VS Code you can add the following to your `mcp.json`:

```json
{
  "mcpServers": {
    "weather": {
      "url": "https://getgather-weather.fly.dev/mcp"
    }
  }
}
```

Clients such as VS Code and Cursor offer true streamable http support (as well as MCP inspector), so there's no need for `npx` or `mcp-remote` commands. 

If you want to test with Claude, it isn't truly using streamable http as the transport, as Claude Desktop doesn't support that yet, but it works fine for testing (claude launches a proxy that hits your endpoint). For example, in Claude Desktop, you can add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "http-weather": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://getgather-weather.fly.dev/mcp",
        "--allow-http"
      ]
    }
  }
}
```

### Run Locally with Docker

Alternatively, you can build the Docker image locally and add the running endpoint to your client config. The following command pulls and runs the latest public image for the weather MCP.

`$ docker run -p 8000:8000 ghcr.io/mcp-getgather/containerized-weather-mcp`

Then add http://localhost:8000/mcp as a model endpoint in your MCP client. If using Claude Desktop, you can add the following to your `claude_desktop_config.json` (which is found from `Claude` -> `Settings` -> `Developer` -> `Edit Config`):

```json
{
  "mcpServers": {
    "http-weather": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "http://127.0.0.1:8000/mcp",
        "--allow-http"
      ]
    }
  }
}
```

If you're not using Claude, and you're client supports http streaming directly, you will just need the local URL and `/mcp` extension as in the VS Code/Cursor example above.

Remember for streamable http (including mcp-remote), you need your mcp server to be running [(as opposed to the client launching it for you as with stdio)](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#stdio).
