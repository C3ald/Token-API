from fastapi import FastAPI, WebSocket
import requests as r
from starlette import websockets
import uvicorn

app = FastAPI()

@app.websocket('/ws')
async def ws(websocket: WebSocket):
	""" p2p example """
	await websocket.accept()
	while True:
		await websockets.send_test('hello world')

if __name__ == '__main__':
	uvicorn.run('p2p:app', host='0.0.0.0', port='999')