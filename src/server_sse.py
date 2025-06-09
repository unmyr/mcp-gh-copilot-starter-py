from fastmcp import FastMCP
import random

mcp = FastMCP(name="sse-test")


@mcp.tool()
def reincarnate(name: str, description="Return reincarnation message") -> str:
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
    mcp.run(transport="sse", host="0.0.0.0", port=8080)
