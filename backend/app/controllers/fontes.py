from fastapi import APIRouter
from app.database import operacoes

router = APIRouter()

@router.get("/fontes")
def listar_fontes():
    """Retorna os dados de rastreabilidade vindos do banco SQLite."""
    fontes_do_banco = operacoes.buscar_fontes()
    
    # Convertendo os resultados do SQLite para uma lista legível
    resultado = [
        {
            "instituicao": f["instituicao"], 
            "url": f["url_documento"], 
            "coleta": f["data_coleta"]
        } for f in fontes_do_banco
    ]
    
    return {"fontes": resultado}