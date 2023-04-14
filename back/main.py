from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import grids, cells, zones, misc


app = FastAPI()

#from database import db
#db.init_db()

app.add_middleware(
	CORSMiddleware,
	allow_origins=['*'],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)
app.include_router(grids.router)
app.include_router(cells.router)
app.include_router(zones.router)
app.include_router(misc.router)
