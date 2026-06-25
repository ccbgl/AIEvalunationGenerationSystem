from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.auth import router as ar
from backend.app.api.auth_me import router as ar_me
from backend.app.api.ai import router as ir
from backend.app.api.shops import router as shops_router
from backend.app.api.products import router as products_router
from backend.app.api.mock_shops import router as mock_shops
from backend.app.api.history import router as history
from backend.app.api.files import router as files
from backend.app.api.evaluations import router as evaluations
from backend.app.api.collection import router as collection
from backend.app.api.admin import router as admin


from backend.app.db.init_db import init_models_and_data
import asyncio

app = FastAPI(title='Sunny Tea House AI 评价系统')

# CORS - allow frontend dev server
# allow common local dev ports used by Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# mount static frontend
app.mount('/static', StaticFiles(directory='backend/app/static'), name='static')

app.include_router(ar)
app.include_router(ar_me)
app.include_router(ir)
# the package exposes router instances directly (see backend.app.api.__init__)
app.include_router(shops_router)
app.include_router(products_router)
app.include_router(mock_shops)
app.include_router(history)
app.include_router(files)
app.include_router(evaluations)
app.include_router(collection)
app.include_router(admin)

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
