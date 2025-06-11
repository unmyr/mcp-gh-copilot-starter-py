from fastmcp import FastMCP
import random

mcp = FastMCP(name="sse-test")


@mcp.tool(name="reincarnate", description="Reincarnate a user with a random message")
def reincarnate(name: str) -> str:
    """Reincarnation function: Receives a user's name and returns a random reincarnation message."""
    messages = [
        f"{name}, you have been reincarnated as a wise old owl.",
        f"{name}, you have been reincarnated as a brave lion.",
        f"{name}, you have been reincarnated as a cheerful dolphin.",
        f"{name}, you have been reincarnated as a skilled musician.",
        f"{name}, you have been reincarnated as a gentle panda.",
    ]
    return random.choice(messages)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--transport", choices=["sse", "stdio"], default="sse", help="Transport type"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host for SSE transport")
    parser.add_argument("--port", type=int, default=3000, help="Port for SSE transport")
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="sse", host=args.host, port=args.port)
