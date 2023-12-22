# DeSSE - Demon's Souls Server Emulator

  A port of the [original desse](https://github.com/ymgve/desse) to modern python

## Overview

Based upon the original work of [Yuvi(ymgve)](https://github.com/ymgve/desse) this port maintains original functionality and expands on the base feature set.



 - Existing Features
	 - Login Messages
	 - Wandering Ghosts
	 - Bloodstains
	 - Messages
	 - Matchmaking
		 - US/EU/JP partitions
 - Bugfixes
	 - Same IP delineation
 - New Features
	 - Integrated DNS server
	 - Auto Public IP Configuration
	 - TOML Config
	 - System ENV Config
	 - Web UI
	 - Web Admin
	 - User/Player Management
	 - TOS Flow Implemented
 - TODO
	 - Virtual Regions
	 - Emulator Detection
	 - Soul Level Matchmaking Control


## Notes
The actual connections between players are facilitated by PSN or RPCN. So long as the respective service is online this server should continue to work.

## Requirements
python 3.11+

## Setup

- run command `pip install -r requirements.txt`

- edit `desse_config.toml` to reflect your public ip in STATUS_SERVER->ip

- if `local_dns_server` is set to `true` ensure all records' ips match the one entered in the step before

- Everyone that wants to connect to the server needs to configure the DNS to point to your DNS proxy in their PS3 network settings.

No other changes should be necessary.
  

## Starting the Server

- run server with `python emulator.py`

## Using System ENV instead of a Config file
To replicate the below toml using system environment variables 

    [SERVER]
    IP = "0.0.0.0"
    PORT = 18000
It should look like this:
|ENV VAR NAME| VALUE |
|--|--|
|SERVER.IP |0.0.0.0|
|SERVER.PORT|18000|