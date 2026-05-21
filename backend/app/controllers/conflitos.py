# -*- coding: utf-8 -*-
from fastapi import APIRouter
from app.database import operacoes

router = APIRouter()

@router.get("/api/conflitos")
def listar_conflitos():
    """Retorna todos os conflitos formatados para o frontend React."""
    return operacoes.buscar_todos_conflitos()

@router.get("/api/conflitos/{id_conflito}")
def obter_conflito(id_conflito: str):
    """Retorna um conflito específico pelo ID."""
    todos = operacoes.buscar_todos_conflitos()
    for c in todos:
        if c["id_conflito"] == id_conflito:
            return c
    return {"erro": "Conflito não encontrado"}
