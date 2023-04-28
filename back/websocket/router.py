from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import Manager


router = APIRouter(
	prefix="/ws",
	tags=["ws"],
)


@router.websocket("/{grid_id}")
async def handle_websocket(grid_id: int, websocket: WebSocket):
	websocket_manager = Manager.get_instance()
	await websocket_manager.connect(websocket, grid_id)
	try:
		while True:
			data = await websocket.receive_text()
			await websocket_manager.send_personal_message(f"You wrote: {data}", websocket)
	except WebSocketDisconnect:
		websocket_manager.disconnect(websocket, grid_id)
		await websocket_manager.broadcast(grid_id, "Client left the chat")
