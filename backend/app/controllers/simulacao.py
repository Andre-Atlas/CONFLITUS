from fastapi import APIRouter
from app.models import ZonaDeImpacto, Coordenada

router = APIRouter()

@router.post("/simular-impacto")
def simular_impacto(latitude: float, longitude: float, intensidade: int, densidade_populacional: int):
    """Calcula e plota as zonas de risco."""
    epicentro = Coordenada(latitude=latitude, longitude=longitude)
    
    zona = ZonaDeImpacto(
        epicentro=epicentro, 
        raio_km=0.0, 
        nivel_risco="Crítico", 
        populacao_afetada=0
    )
    
    zona.calcular_raio(intensidade)
    zona.estimar_impacto_humanitario(densidade_populacional)
    
    return {"mensagem": "Impacto calculado com sucesso", "dados": zona}