from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import Manager


router = APIRouter(
	prefix="/ws",
	tags=["ws"],
)


manager = Manager.get_instance()


@router.websocket("/{grid_id}")
async def websocket(grid_id: int, ws: WebSocket):
	await manager.connect(ws, grid_id)
	try:
		while True:
			data = await ws.receive_text()
			await manager.send_personal_message(f"You wrote: {data}", ws)
	except WebSocketDisconnect:
		manager.disconnect(ws, grid_id)
		await manager.broadcast(grid_id, "Client left the chat")
