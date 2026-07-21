from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.v1.schemas.auth import (
    UsuarioRegistro, UsuarioRespuesta, Token
)
from api.dependencies import crear_token, get_usuario_actual

router = APIRouter(prefix='/auth', tags=['Autenticación'])

@router.post(
    '/registro',
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED
)
def registro(datos: UsuarioRegistro):
    """Crea una cuenta nueva en AgriGestor"""
    from apps.usuarios.models import Usuario
    
    # Verifica que el username no esté tomado
    if Usuario.objects.filter(username=datos.username).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='El nombre de usuario ya está en uso'
        )
    
    # Verifica que le email no esté tomado
    if Usuario.objects.filter(email=datos.email).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='El correo electrónico ya está en uso'
        )
    
    # Valida que el rol sea válido
    roles_validos = ['agricultor', 'tecnico', 'admin']
    if datos.rol not in roles_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Rol inválido. Opciones: {roles_validos}'
        )
    
    usuario = Usuario(
        username = datos.username,
        email = datos.email,
        password = datos.password,
        first_name = datos.first_name,
        last_name = datos.last_name,
        rol = datos.rol,
        telefono = datos.telefono,
        municipio = datos.municipio,
    )
    usuario.set_password(datos.password) # hashea correctamente
    usuario.save()
    return usuario

@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    from apps.usuarios.models import Usuario

    # Busca el usuario directamente en la BD
    try:
        usuario = Usuario.objects.get(username=form_data.username)
    except Usuario.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Usuario o contraseña incorrectos',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # Verifica la contraseña usando el método del modelo de Django
    if not usuario.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Usuario o contraseña incorrectos',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cuenta inactiva'
        )

    token = crear_token(data={'sub': usuario.username})
    return {'access_token': token, 'token_type': 'bearer'}

@router.get('/yo', response_model=UsuarioRespuesta)
def yo(usuario=Depends(get_usuario_actual)):
    """
    Endpoint protegido - devuelve los datos del usuario autenticado.
    Sirve para verificar que el token funciona correctamente.
    """
    return usuario