import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import get_manager


router = APIRouter(
	prefix="/ws",
	tags=["ws"],
)


manager = get_manager()


@router.websocket("/{grid_id}")
async def websocket(grid_id: int, websocket: WebSocket):
	await manager.connect(websocket, grid_id)
	try:
		while True:
			data = await websocket.receive_text()
			await manager.send_personal_message(f"You wrote: {data}", websocket)
	except WebSocketDisconnect:
		manager.disconnect(websocket, grid_id)
		await manager.broadcast(f"Client left the chat")
