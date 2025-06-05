from mcp.server.fastmcp import FastMCP

mcp = FastMCP("simple-mcp-server")


@mcp.tool(name="add", description="Add two numbers")
async def add(a: int, b: int) -> int:
    return a + b


@mcp.tool(name="subtract", description="Subtract two numbers")
async def subtract(a: int, b: int) -> int:
    return a - b


if __name__ == "__main__":
    mcp.run(transport="stdio")
