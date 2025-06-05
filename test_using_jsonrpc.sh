#!/usr/bin/expect -f
set timeout 10

spawn python src/server.py
send -- "{\"jsonrpc\": \"2.0\", \"id\": 0, \"method\": \"initialize\", \"params\": {\"protocolVersion\": \"2024-11-05\", \"capabilities\": {}, \"clientInfo\": {\"name\": \"whatever\", \"version\": \"0.0.0\"}}}\r"
expect \"result\"

send --  "{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\",\"params\":{}}\r"
expect \"result\"

send -- "{\"jsonrpc\": \"2.0\", \"id\": 0, \"method\": \"tools/list\", \"params\":{}}\r"
expect \"result\"

send -- "{\"jsonrpc\": \"2.0\", \"id\": 0, \"method\": \"tools/call\", \"params\":{\"name\": \"add\", \"arguments\": {\"a\": 1, \"b\": 3}}}\r"
expect \"result\"
exit
