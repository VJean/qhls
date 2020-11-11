#!/usr/bin/env python3

import re
import socket
from datetime import datetime
import pandas as pd
import argparse
from progress.bar import Bar

def int_gte_one(string):
    value = int(string)
    if value < 1:
        raise argparse.ArgumentTypeError("%r must be greater than 0" % string)
    return value

parser = argparse.ArgumentParser(description='Display stats from a HTTP log file.')
parser.add_argument('logfile', help="the logfile to parse")
parser.add_argument('--limit', dest="limit", default=None, type=int, help='maximum number of lines to parse from the file')
parser.add_argument('--top-size', dest="top_size", default=5, type=int_gte_one, help='number of items in displayed rankings')

args = parser.parse_args()

limit = len(open(args.logfile).readlines())

if args.limit is not None and args.limit < limit:
    limit = args.limit

my_nginx_regex = '^(?P<remote_addr>.+?) - (?:-|(?P<user>.+?)) \[(?P<timestamp>.+?)\] \"(?P<request>.+?)\" (?P<status>\d{3}) (?P<bytes_sent>\d+?) (?P<duration>\d+\.\d+) \"(?P<referer>.+?)" \"(?:-|(?P<user_agent>.+))\"$'
pattern = re.compile(my_nginx_regex)

parsed_lines = []

with Bar('Processing log lines', max=limit) as bar:
    with open(args.logfile, 'r') as logs:
        line_number = 0
        for log_line in logs:
            if line_number == limit:
                break
            line_number += 1
            match = pattern.match(log_line)
            if match:
                d = match.groupdict()
                d['ts'] = datetime.fromisoformat(d['timestamp'])
                d['status'] = int(d['status'])
                d['bytes_sent'] = int(d['bytes_sent'])
                d['duration'] = float(d['duration'])

                # try to resolve remote addr
                try :
                    name, *_ = socket.gethostbyaddr(d['remote_addr'])
                    d['remote_host'] = name
                except socket.herror as e:
                    # d['remote_host'] = '_no_host_found'
                    pass

                parsed_lines.append(d)
                bar.next()


df = pd.DataFrame(parsed_lines, columns=["ts","remote_addr","remote_host","status","duration","user_agent"])
df.to_csv('./data.csv')


def display_top(series):
    top = series.value_counts(dropna=True).head(args.top_size)
    for label, count in top.items():
        print(f"{count}\t{label}")
    return top

print()
print(f"{len(df)} records from {df['ts'].min()} to {df['ts'].max()}")

print()
print(f"Global response time : min={df['duration'].min():.3f}s, mean={df['duration'].mean():.3f}s, max={df['duration'].max():.3f}s")

# free some memory
df.drop(columns='ts',inplace=True)

df_status = df[['status','duration']].groupby('status')

print("Response time by status :")
print("status\tmin\tmean\tmax")
for status, _ in df_status:
    print(f"{status}\t{df[df.status == status]['duration'].min():.3f}s\t{df[df.status == status]['duration'].mean():.3f}s\t{df[df.status == status]['duration'].max():.3f}s")

# free some memory
df.drop(columns=['duration','status'],inplace=True)
del df_status

df['client'] = df['remote_addr'] + ' (' + df['remote_host'].fillna('_no_host_found') + ')'
print()
print("Top clients :")
top_clients = display_top(df["client"])

print()
print("User agents of each top client (might be empty) :")
clients_uagents = df[["client","user_agent"]]
for client, _ in top_clients.items():
    print(f"=> {client}")
    display_top(clients_uagents[clients_uagents.client == client]['user_agent'])
