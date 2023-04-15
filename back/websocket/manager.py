from typing import List
from fastapi import WebSocket


manager = None


class Manager:
	def __init__(self):
		self._connections: Dict[int, List[WebSocket]] = {}


	async def connect(self, websocket: WebSocket, grid: int):
		await websocket.accept()
		if (grid not in self._connections):
			self._connections[grid] = []
		self._connections[grid].append(websocket)


	def disconnect(self, websocket: WebSocket, grid):
		self._connections[grid].remove(websocket)


	async def send_personal_message(self, message: str, websocket: WebSocket):
		await websocket.send_text(message)


	async def broadcast(self, grid: int, message: str):
		if (grid not in self._connections):
			return
		for connection in self._connections[grid]:
			await connection.send_text(message)


def get_manager():
	global manager
	if (manager is None):
		manager = Manager()
	return manager
