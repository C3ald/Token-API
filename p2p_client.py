import asyncio
import websockets
import requests as r
import time as t



URL = 'token-network.herokuapp.com'
SHOW_NODES = f'https://{URL}/show_nodes'
WS = f'ws://{URL}/ws'
ADD_NODE = f'https://{URL}/add_node'
NODES = []
CLIENT_NODE = []

def get_ip():
	ip = r.get('https://api.ipify.org').content.decode('utf8')
	print(ip)
	CLIENT_NODE.append(ip)
	return ip

async def ws():
	async with websockets.connect(WS) as websocket:
		await websocket.recv()
		t.sleep(0.5)

async def add_node():
	# async with websockets.connect(URL) as websocket:
	# 	await None
	node = get_ip()
	all_nodes = r.get('https://{URL}/show_nodes')
	add_node = r.post('https://{URL}/add_node/',json={'nodes': node})


# asyncio.run(ws())
get_ip()
print({'ip':NODES})