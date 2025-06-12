import asyncio
import json
import sys
import traceback


async def read_error(error_reader, timeout=0.2):
    try:
        stderr = await asyncio.wait_for(error_reader.read(), timeout=timeout)
        if stderr:
            return stderr.decode("utf-8")
    except asyncio.TimeoutError:
        pass
    return None


async def send_jsonrpc(writer, payload):
    try:
        message = json.dumps(payload)
        writer.write((message + "\n").encode("utf-8"))
        # print("Sending JSON-RPC message:", repr(message), flush=True)
        await writer.drain()
    except (BrokenPipeError, ConnectionResetError) as e:
        if str(e) == "Connection lost":
            return None
        print(traceback.format_exc(), flush=True, file=sys.stderr)


async def read_response(reader):
    # Read until the end of the line
    try:
        chunk = await reader.readuntil(b"\n")
        if not chunk:
            return None

    except asyncio.IncompleteReadError as _e:
        return None

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
        "src/tool_reincarnate.py",
        "--transport",
        "stdio",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        text=False,
        close_fds=True,
    )
    seq_id = 0

    # 1. initialize
    _, stderr = await asyncio.gather(
        send_jsonrpc(
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
        ),
        read_error(proc.stderr, 0),
    )
    if stderr:
        print(stderr, flush=True, file=sys.stderr)
        sys.exit(1)

    resp, stderr = await asyncio.gather(
        read_response(proc.stdout), read_error(proc.stderr, 0)
    )
    if stderr:
        print(stderr, flush=True, file=sys.stderr)
        sys.exit(1)
    print("initialize result:", resp)

    # 2. notifications/initialized
    _, stderr = await asyncio.gather(
        send_jsonrpc(
            proc.stdin,
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        ),
        read_error(proc.stderr, 0.2 if resp is None else 0),
    )
    if stderr:
        print(stderr, flush=True, file=sys.stderr)
        sys.exit(1)
    # This notification does not expect a response

    # 3. tools/list
    print()
    seq_id += 1
    _, stderr = await asyncio.gather(
        send_jsonrpc(
            proc.stdin,
            {"jsonrpc": "2.0", "id": seq_id, "method": "tools/list", "params": {}},
        ),
        read_error(proc.stderr, 0.2 if resp is None else 0),
    )
    if stderr:
        print(stderr, flush=True, file=sys.stderr)
        sys.exit(1)

    resp, stderr = await asyncio.gather(
        read_response(proc.stdout), read_error(proc.stderr, 0)
    )
    if stderr:
        print(stderr, flush=True, file=sys.stderr)
        sys.exit(1)

    print("tools/list result:", resp)

    # 4. tools/call (reincarnate)
    print()
    seq_id += 1
    _, stderr = await asyncio.gather(
        send_jsonrpc(
            proc.stdin,
            {
                "jsonrpc": "2.0",
                "id": seq_id,
                "method": "tools/call",
                "params": {"name": "reincarnate", "arguments": {"name": "Ann"}},
            },
        ),
        read_error(proc.stderr, 0.2 if resp is None else 0),
    )
    if stderr:
        print(stderr, flush=True, file=sys.stderr)
        sys.exit(1)

    resp, stderr = await asyncio.gather(
        read_response(proc.stdout), read_error(proc.stderr, 0)
    )
    if stderr:
        print(stderr, flush=True, file=sys.stderr)
        sys.exit(1)

    print("tools/call add result:", resp)

    # 5. resources/list
    print()
    seq_id += 1
    _, stderr = await asyncio.gather(
        send_jsonrpc(
            proc.stdin,
            {
                "jsonrpc": "2.0",
                "id": seq_id,
                "method": "resources/list",
            },
        ),
        read_error(proc.stderr, 0.2 if resp is None else 0),
    )
    if stderr:
        print(stderr, flush=True, file=sys.stderr)
        sys.exit(1)

    resp, stderr = await asyncio.gather(
        read_response(proc.stdout), read_error(proc.stderr, 0)
    )
    if stderr:
        print(stderr, flush=True, file=sys.stderr)
        sys.exit(1)
    print("resources/list add result:", resp)

    # 6. prompts/list
    print()
    seq_id += 1
    _, stderr = await asyncio.gather(
        send_jsonrpc(
            proc.stdin,
            {
                "jsonrpc": "2.0",
                "id": seq_id,
                "method": "prompts/list",
            },
        ),
        read_error(proc.stderr, 0.2 if resp is None else 0),
    )
    if stderr:
        print(stderr, flush=True, file=sys.stderr)
        sys.exit(1)

    resp, stderr = await asyncio.gather(
        read_response(proc.stdout), read_error(proc.stderr, 0)
    )
    if stderr:
        print(stderr, flush=True, file=sys.stderr)
        sys.exit(1)
    print("prompts/list add result:", resp)

    # 7. server.shutdown
    seq_id += 1
    _, stderr = await asyncio.gather(
        send_jsonrpc(
            proc.stdin,
            {"jsonrpc": "2.0", "id": seq_id, "method": "server.shutdown", "params": []},
        ),
        read_error(proc.stderr, 0.2 if resp is None else 0),
    )
    if stderr:
        print(f"ERROR: {stderr}", flush=True, file=sys.stderr)
        sys.exit(1)
    # Optionally read shutdown response

    proc.stdin.close()
    await asyncio.sleep(0.1)  # Give some time for the process to handle the shutdown
    await proc.wait()


async def main():
    await main_task()


if __name__ == "__main__":
    asyncio.run(main())
