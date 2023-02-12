A very very quick and dirty python3 port of desse; It's not done yet but soon:tm:

DeSSE - Demon's Souls Server Emulator

This is a very quick and dirty server emulator that supports the most basic features.
Working at the moment:

 - matchmaking (only internally in each region, EU/US/JP people won't see each other's summon signs for example)
 - messages, pre-seeded with some old EU messages, but new messages have priority
 - ghosts
 - bloodstains, pre-seeded with some old EU stains, new stains have priority
 
The matchmaking only works by virtue of Sony's matchmaking servers being online. I don't know
if these servers are generic and will continue working in the future or if they might
be turned off at some point. It works right now, at least.
 
Requirements:

 - python 3.10.8+
 - cryptography,dnserver
 

Setup:
 - run command `pip install cryptography dnserver`
 - edit `des_emu_config.json` to reflect your public ip in INFO_SS->ip
 - if `local_dns_server` is set to `true` ensure all records' ips match the one entered in the step before

Starting the Server
 - run server with `python emulator.py`
 
Everyone that wants to connect to the server needs to configure the DNS to point to your DNS proxy in their PS3 network settings.
No other changes should be necessary.
