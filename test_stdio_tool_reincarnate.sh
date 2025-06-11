#!/usr/bin/expect -f
set timeout 10

spawn python src/tool_reincarnate.py --transport stdio
send -- "{\"jsonrpc\": \"2.0\", \"id\": 0, \"method\": \"initialize\", \"params\": {\"protocolVersion\": \"2024-11-05\", \"capabilities\": {}, \"clientInfo\": {\"name\": \"whatever\", \"version\": \"0.0.0\"}}}\r"
expect  {
    -r "\r\n" {puts "Received response to initialize"}
    timeout {
        puts "ERROR: Timeout occurred while waiting for response to initialize"
        exit 1
    }
}
expect "result"

send --  "{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\",\"params\":{}}\r"

puts ""
send -- "{\"jsonrpc\": \"2.0\", \"id\": 0, \"method\": \"tools/list\", \"params\":{}}\r"
expect  {
    -r "\r\n" {puts "Received response to tools/list"}
    timeout {
        puts "ERROR: Timeout occurred while waiting for tools/list"
        exit 1
    }
}
expect "result"

puts ""
send -- "{\"jsonrpc\": \"2.0\", \"id\": 0, \"method\": \"tools/call\", \"params\":{\"name\": \"reincarnate\", \"arguments\": {\"name\": \"Ann\"}}}\r"
expect {
  -r "\r\n" {
    puts "Received response to tools/call"
}
 timeout {
        puts "ERROR: Timeout occurred while waiting for response to tools/call"
        exit 1
    }
}
expect "result"

puts ""
send -- "{\"jsonrpc\": \"2.0\", \"id\": 0, \"method\": \"resources/list\", \"params\":{}}\r"
expect {
  -r "\r\n" {
    puts "Received response to resources/list"
}
 timeout {
        puts "ERROR: Timeout occurred while waiting for response to resources/list"
        exit 1
    }
}
expect "result"

puts ""
send -- "{\"jsonrpc\": \"2.0\", \"id\": 0, \"method\": \"prompts/list\"}\r"
expect {
  -r "\r\n" {
    puts "Received response to prompts/list"
    expect "result"
}
 timeout {
        puts "ERROR: Timeout occurred while waiting for response to prompts/list"
        exit 1
    }
}

puts ""
send --  "{\"jsonrpc\":\"2.0\", \"id\": 0, \"method\":\"server.shutdown\",\"params\":[]}\r"

exit