# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import simulacao, rotas, fontes, conflitos, acolhimento
from app.database import operacoes
from app.pipeline import PipelineDeDados

app = FastAPI(
    title="CONFLITUS - Observatório Geopolítico",
    description="API do observatório geopolítico interativo que mapeia e detalha zonas de conflito."
)

# CORS para permitir o frontend acessar a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conecta os controllers
app.include_router(conflitos.router, tags=["Conflitos"])
app.include_router(simulacao.router, tags=["Simulação de Impacto"])
app.include_router(rotas.router, tags=["Análise de Rotas"])
app.include_router(fontes.router, tags=["Transparência e Fontes"])
app.include_router(acolhimento.router, tags=["Rotas de Acolhimento"])

@app.on_event("startup")
def startup_event():
    """Inicializa o banco e carrega dados seed se necessário."""
    operacoes.inicializar_tabelas()
    if not operacoes.tem_conflitos():
        print("[Startup] Banco vazio. Carregando dados seed...")
        pipeline = PipelineDeDados()
        pipeline.carregar_seed_data()
        print("[Startup] Dados seed carregados com sucesso!")
    else:
        # Se os conflitos já existem, calcula/atualiza as estimativas e tendências via ML
        from app.ml import atualizar_todas_previsoes
        try:
            atualizar_todas_previsoes()
        except Exception as e:
            print(f"[Startup] Falha ao calcular previsões via ML no startup: {e}")


@app.get("/")
def home():
    """Endpoint de boas-vindas."""
    return {"mensagem": "Bem-vindo à API do projeto CONFLITUS!"}

@app.post("/api/pipeline/executar")
def executar_pipeline():
    """Executa o pipeline completo de enriquecimento de dados (ACLED + UCDP)."""
    try:
        pipeline = PipelineDeDados()
        pipeline.executar_carga_completa()
        return {"mensagem": "Pipeline executado com sucesso!", "status": "ok"}
    except Exception as e:
        return {"mensagem": f"Erro no pipeline: {str(e)}", "status": "erro"}