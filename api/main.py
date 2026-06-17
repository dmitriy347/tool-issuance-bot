from fastapi import FastAPI

from api.routers.employees import router as employees_router
from api.routers.inventories import router as inventories_router
from api.routers.documents import router as documents_router

app = FastAPI()

app.include_router(employees_router, prefix="/api")
app.include_router(inventories_router, prefix="/api")
app.include_router(documents_router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "ok"}