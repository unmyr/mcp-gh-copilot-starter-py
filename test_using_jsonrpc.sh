#!/usr/bin/expect -f
set timeout 10

set t0 [clock seconds]
spawn python src/server.py
send -- "{\"jsonrpc\": \"2.0\", \"id\": 0, \"method\": \"initialize\", \"params\": {\"protocolVersion\": \"2024-11-05\", \"capabilities\": {}, \"clientInfo\": {\"name\": \"whatever\", \"version\": \"0.0.0\"}}}\r"
expect \"result\"

send --  "{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\",\"params\":{}}\r"
set t1 [clock seconds]

set elapsed_time [expr {$t1 - $t0}]
puts "Elapsed time for Initialize: $elapsed_time seconds"

send -- "{\"jsonrpc\": \"2.0\", \"id\": 0, \"method\": \"tools/list\", \"params\":{}}\r"
expect \"result\"

send -- "{\"jsonrpc\": \"2.0\", \"id\": 0, \"method\": \"tools/call\", \"params\":{\"name\": \"add\", \"arguments\": {\"a\": 1, \"b\": 3}}}\r"
expect \"result\"
set t2 [clock seconds]

set elapsed_time_initialize [expr {$t2 - $t1}]
puts "Elapsed time for call: $elapsed_time seconds"

send --  "{\"jsonrpc\":\"2.0\", \"id\": 0, \"method\":\"server.shutdown\",\"params\":[]}\r"
# expect \"result\"

exit
