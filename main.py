from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.get.usuarios import router as usuarios_router
from routes.set.deshabilitar_usuario import router as deshabilitar_usuario_router
from routes.set.habilitar_usuario import router as habilitar_usuario_router
from routes.delete.eliminar_usuario import router as eliminar_usuario_router
from routes.create.crear_usuario import router as crear_usuario_router
from routes.auth.login import router as login_router
from routes.auth.cambiar_pass import router as cambiar_pass_router
from routes.bootstrap import router as bootstrap_router
import os

from dotenv import load_dotenv
from bootstrap import bootstrap

load_dotenv()

bootstrap()

app = FastAPI(title="API mortadela", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://{os.getenv('FRONTEND_IP')}:3000",
        "http://localhost:3000",
        "http://192.168.20.53:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios_router)
app.include_router(deshabilitar_usuario_router)
app.include_router(habilitar_usuario_router)
app.include_router(eliminar_usuario_router)
app.include_router(crear_usuario_router)
app.include_router(login_router)
app.include_router(cambiar_pass_router)
app.include_router(bootstrap_router)

@app.get("/")
def hola():
    return {"mensaje": "API AUTH"}