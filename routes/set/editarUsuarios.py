from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import get_connection
from auth import get_current_user, TokenUser
import bcrypt

router = APIRouter(tags=["usuarios"])

class EditarUsuarioData(BaseModel):
    id: int
    username: str
    email: EmailStr
    nombre: str
    apellido: str
    rol: str
    password: Optional[str] = None
    reporte: bool
    habilitado: int

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None

@router.post("/editar_usuario", response_model=ApiResponse)
def editar_usuario(data: EditarUsuarioData, current_user: TokenUser = Depends(get_current_user)) -> ApiResponse:
    # Verificar permisos: usuarios con rol 'user' no pueden editar usuarios
    if not current_user.get("rol") or current_user.get("rol") == "user":
        raise HTTPException(status_code=403, detail="No tenés permiso para modificar usuarios")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verificar que el usuario existe
        cursor.execute(
            "SELECT rol FROM Usuarios WHERE id = %s",
            (data.id,)
        )
        usuario = cursor.fetchone()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # No permitir editar superadmin
        if usuario["rol"] == "superadmin":
            raise HTTPException(
                status_code=403,
                detail="No se puede editar un superadmin"
            )

        # Verificar que email no esté duplicado (excepto el del usuario actual)
        cursor.execute(
            """
            SELECT 1 FROM Usuarios 
            WHERE email = %s AND id != %s
            """,
            (data.email, data.id)
        )
        
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="El email ya existe"
            )

        # Verificar que username no esté duplicado (excepto el del usuario actual)
        cursor.execute(
            """
            SELECT 1 FROM Usuarios 
            WHERE username = %s AND id != %s
            """,
            (data.username, data.id)
        )
        
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="El username ya existe"
            )

        # Preparar actualización
        update_fields = []
        update_values = []

        update_fields.append("username = %s")
        update_values.append(data.username)

        update_fields.append("email = %s")
        update_values.append(data.email)

        update_fields.append("nombre = %s")
        update_values.append(data.nombre)

        update_fields.append("apellido = %s")
        update_values.append(data.apellido)

        update_fields.append("rol = %s")
        update_values.append(data.rol)

        update_fields.append("reporte = %s")
        update_values.append(int(data.reporte))

        update_fields.append("habilitado = %s")
        update_values.append(data.habilitado)

        # Si se proporciona password, hashear e incluir
        if data.password:
            hashed_password = bcrypt.hashpw(
                data.password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")
            update_fields.append("password_hash = %s")
            update_values.append(hashed_password)

        # Agregar id al final para el WHERE
        update_values.append(data.id)

        query = f"""
            UPDATE Usuarios 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """

        cursor.execute(query, update_values)
        conn.commit()

        return ApiResponse(success=True, message="Usuario actualizado correctamente")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
