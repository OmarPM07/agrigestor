from config.django_app import setup_django
setup_django()

from fastapi import FastAPI
from api.v1.routers import auth, parcelas, cultivos, insumos, reportes

app = FastAPI(
    title='AgriGestor API',
    description='Sistema de gestión de parcelas agrícolas - Nayarit, México',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc',
)

app.include_router(auth.router, prefix='/api/v1')
app.include_router(parcelas.router, prefix='/api/v1')
app.include_router(cultivos.router, prefix='/api/v1')
app.include_router(insumos.router,  prefix='/api/v1')
app.include_router(reportes.router, prefix='/api/v1')

@app.get('/', tags=['Root'])
def raiz():
    return {
        'proyecto': 'AgriGestor',
        'version': '1.0.0',
        'docs': '/docs',
    }