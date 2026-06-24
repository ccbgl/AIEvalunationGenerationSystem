from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.app.api import auth, ai
from backend.app.db.init_db import init_models_and_data
import asyncio

app = FastAPI(title='Sunny Tea House AI 评价系统')

# mount static frontend
app.mount('/static', StaticFiles(directory='backend/app/static'), name='static')

app.include_router(auth.router)
app.include_router(ai.router)

@app.on_event('startup')
async def startup_event():
    # initialize DB and default data
    try:
        await init_models_and_data()
    except Exception as e:
        print('DB init warning:', e)

@app.get('/')
async def root():
    return {"message": "Sunny Tea House API"}
