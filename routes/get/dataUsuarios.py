from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import get_connection
from auth import get_current_user, TokenUser

router = APIRouter(tags=["usuarios"])

class DatosUsuarioResponse(BaseModel):
    id: int
    email: str
    username: str
    nombre: str
    apellido: str
    rol: str
    reporte: bool
    habilitado: int

@router.get("/data_usuario/{username}", response_model=DatosUsuarioResponse)
def obtener_datos_usuario(username: str, current_user: TokenUser = Depends(get_current_user)):
    # Verificar permisos: solo admin, superadmin o el mismo usuario puede ver sus datos
    if current_user.get("rol") == "user" and current_user.get("username") != username:
        raise HTTPException(status_code=403, detail="No tenés permiso para ver estos datos")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id, email, username, nombre, apellido, rol, habilitado, reporte 
            FROM Usuarios 
            WHERE username = %s
            """,
            (username,)
        )
        usuario = cursor.fetchone()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return DatosUsuarioResponse(
            id=usuario["id"],
            email=usuario["email"],
            username=usuario["username"],
            nombre=usuario["nombre"],
            apellido=usuario["apellido"],
            rol=usuario["rol"],
            reporte=bool(usuario["reporte"]),
            habilitado=usuario["habilitado"]
        )
    finally:
        cursor.close()
        conn.close()
