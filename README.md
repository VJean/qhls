# Quick HTTP Logs Stats

## Usage

```
$ ./qhls.py example.log -h
usage: qhls.py [-h] [--limit LIMIT] [--top-size TOP_SIZE] logfile

Display stats from a HTTP log file.

positional arguments:
  logfile              the logfile to parse

optional arguments:
  -h, --help           show this help message and exit
  --limit LIMIT        maximum number of lines to parse from the file
  --top-size TOP_SIZE  number of items in displayed rankings
```

## Run it yourself

To run it against your own logs, you'll have to modify the regex in the script to match your own log format.

Just keep the following named capture groups :
* `ts` - the timestamp (which is expected to be an ISO8601 formatted date, if that's not the case modify line 43 accordingly)
* `remote_addr` - the client ip
* `status` - the HTTP status code
* `duration` - the request duration in seconds
* `user_agent` - the User Agent used by the client

## Example output

Example output :

```
$ ./qhls.py example.log --limit 500 --top-size 3
Processing log lines |################################| 500/500

500 records from 2020-11-07 01:03:56+01:00 to 2020-11-07 08:55:46+01:00

Global response time : min=0.000s, mean=0.015s, max=2.676s
Response time by status :
status  min mean    max
200 0.000s  0.016s  0.361s
400 0.000s  0.153s  0.536s
404 0.000s  0.014s  2.676s

Top clients :
462 123.123.123.123 (_no_host_found)
9   234.234.234.234 (_no_host_found)
2   345.345.345.345 (***)

User agents of each top client (might be empty) :
=> 123.123.123.123 (_no_host_found)
297 Mozilla/5.0 (Windows NT 6.1 ...
140 Mozilla/5.0 (Windows NT 5.2 ...
10  Mozilla/5.0 (X11; Linux x86_64...
=> 234.234.234.234 (_no_host_found)
9   Mozilla/5.0 (Windows NT 10.0...
=> 345.345.345.345 (***)
```

