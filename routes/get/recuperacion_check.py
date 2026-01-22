from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from database import get_connection
from typing import Dict, Any, Optional, cast
import requests
import os

router = APIRouter(tags=["usuarios"])

class RecuperacionRequest(BaseModel):
  username: str
  email: EmailStr

@router.post("/recuperacionCheck")
def check_user_email(data: RecuperacionRequest):
  conn = get_connection()
  cursor = conn.cursor(dictionary=True)

  try:
    cursor.execute(
      "SELECT username, email, nombre, apellido FROM Usuarios WHERE username = %s AND email = %s",
      (data.username, data.email)
    )
    user = cast(Optional[Dict[str, Any]], cursor.fetchone())

    if user:
      mail_api_url = os.getenv("NEXT_PUBLIC_API_MAIL_URL")
      if mail_api_url:
        try:
          recuperacion_url = f"{mail_api_url}/recuperacion"
          payload: Dict[str, str] = {
            "nombre": str(user["nombre"]),
            "apellido": str(user["apellido"]),
            "email": str(user["email"])
          }
          requests.post(recuperacion_url, json=payload)
        except Exception as e:
          print(f"Error al enviar email de recuperación: {str(e)}")
      
      return JSONResponse(
        content={
          "success": True,
          "message": "Usuario y correo verificados correctamente"
        },
        status_code=200
      )
    else:
      return JSONResponse(
        content={
          "success": False,
          "error": "El usuario y correo no coinciden o no existen"
        },
        status_code=404
      )

  except Exception as e:
    return JSONResponse(
      content={
        "success": False,
        "error": f"Error al verificar los datos: {str(e)}"
      },
      status_code=500
    )
  finally:
    cursor.close()
    conn.close() 
