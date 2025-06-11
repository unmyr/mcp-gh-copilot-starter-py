import asyncio
import json


async def send_jsonrpc(writer, payload):
    message = json.dumps(payload)
    writer.write((message + "\n").encode("utf-8"))
    # print("Sending JSON-RPC message:", repr(message), flush=True)
    await writer.drain()


async def read_response(reader):
    # Read until the end of the line
    chunk = await reader.readuntil(b"\n")
    if not chunk:
        raise EOFError("Unexpected end of stream while reading header")
    if chunk.startswith(b"{"):
        body = chunk
    else:
        body = chunk
        while not body.endswith(b"]\n"):
            chunk = await reader.readuntil(b"\n")
            if not chunk:
                raise EOFError("Unexpected end of stream while reading header")
            body += chunk
    # print("body:", repr(body), flush=True)
    return json.loads(body.decode("utf-8"))


async def main_task():
    # Start the server process via pseudo-terminal
    proc = await asyncio.create_subprocess_exec(
        "python",
        "src/tool_simple_math.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        text=False,
        close_fds=True,
    )
    seq_id = 0

    # 1. initialize
    await send_jsonrpc(
        proc.stdin,
        {
            "jsonrpc": "2.0",
            "id": seq_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "whatever", "version": "0.0.0"},
            },
        },
    )
    resp = await read_response(proc.stdout)
    print("initialize result:", resp)

    # 2. notifications/initialized
    await send_jsonrpc(
        proc.stdin,
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
    )
    # This notification does not expect a response

    # 3. tools/list
    print()
    seq_id += 1
    await send_jsonrpc(
        proc.stdin,
        {"jsonrpc": "2.0", "id": seq_id, "method": "tools/list", "params": {}},
    )
    resp = await read_response(proc.stdout)
    print("tools/list result:", resp)

    # 4. tools/call (add)
    print()
    seq_id += 1
    await send_jsonrpc(
        proc.stdin,
        {
            "jsonrpc": "2.0",
            "id": seq_id,
            "method": "tools/call",
            "params": {"name": "add", "arguments": {"a": 1, "b": 3}},
        },
    )
    resp = await read_response(proc.stdout)
    print("tools/call add result:", resp)

    # 5. resources/list
    print()
    seq_id += 1
    await send_jsonrpc(
        proc.stdin,
        {
            "jsonrpc": "2.0",
            "id": seq_id,
            "method": "resources/list",
        },
    )
    resp = await read_response(proc.stdout)
    print("resources/list add result:", resp)

    # 6. prompts/list
    print()
    seq_id += 1
    await send_jsonrpc(
        proc.stdin,
        {
            "jsonrpc": "2.0",
            "id": seq_id,
            "method": "prompts/list",
        },
    )
    resp = await read_response(proc.stdout)
    print("prompts/list add result:", resp)

    # 7. server.shutdown
    print()
    seq_id += 1
    await send_jsonrpc(
        proc.stdin,
        {"jsonrpc": "2.0", "id": seq_id, "method": "server.shutdown", "params": []},
    )
    # Optionally read shutdown response

    proc.stdin.close()
    await asyncio.sleep(0.1)  # Give some time for the process to handle the shutdown
    await proc.wait()


async def main():
    await main_task()


if __name__ == "__main__":
    asyncio.run(main())
