from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="ERP Help Assistant")
app.include_router(router)
