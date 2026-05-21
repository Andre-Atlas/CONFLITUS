# -*- coding: utf-8 -*-
import numpy as np
from sklearn.linear_model import LinearRegression
from app.database.conexao import get_db_connection

def prever_tendencia_conflito(id_conflito):
    """
    Usa Scikit-Learn (LinearRegression) e NumPy para analisar a série temporal
    de fatalidades mensais e estimar a tendência e as fatalidades previstas para o próximo mês.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Busca os dados do gráfico mensal ordenados por ID (cronológico)
    dados = cursor.execute(
        'SELECT mes, fatalidades FROM dados_grafico_mensal WHERE id_conflito = ? ORDER BY id',
        (id_conflito,)
    ).fetchall()
    
    conn.close()
    
    if not dados or len(dados) < 3:
        # Sem histórico suficiente para treinar um modelo coerente
        return 0, "Estável"
        
    # Prepara os dados para o Scikit-Learn
    # X: Índices dos meses (0, 1, 2...)
    # y: Número de fatalidades correspondente
    X = np.arange(len(dados)).reshape(-1, 1)
    y = np.array([row["fatalidades"] for row in dados])
    
    # Treina o modelo de regressão linear simples
    modelo = LinearRegression()
    modelo.fit(X, y)
    
    # Prediz as fatalidades para o próximo mês (índice len(dados))
    proximo_mes_idx = len(dados)
    previsao = modelo.predict([[proximo_mes_idx]])[0]
    
    # Garante que a previsão não seja negativa
    previsao_final = max(0, int(round(previsao)))
    
    # Determina a tendência a partir do coeficiente angular (slope)
    slope = modelo.coef_[0]
    
    # Se a variação mensal média for relevante (> 5% da média de mortes ou absoluta)
    media_fatalidades = np.mean(y) if len(y) > 0 else 1
    variacao_relativa = slope / media_fatalidades if media_fatalidades > 0 else 0
    
    if slope > 15 or variacao_relativa > 0.05:
        tendencia = "Crescente"
    elif slope < -15 or variacao_relativa < -0.05:
        tendencia = "Decrescente"
    else:
        tendencia = "Estável"
        
    return previsao_final, tendencia

def atualizar_todas_previsoes():
    """
    Roda a previsão de tendências de ML para todos os conflitos cadastrados e atualiza o banco.
    """
    print("\n[ML] Iniciando atualização de previsões e análise de tendências via Scikit-Learn...")
    conn = get_db_connection()
    cursor = conn.cursor()
    conflitos = cursor.execute('SELECT id_conflito, pais FROM conflitos').fetchall()
    conn.close()
    
    for c in conflitos:
        cid = c["id_conflito"]
        previsao, tendencia = prever_tendencia_conflito(cid)
        
        # Atualiza a tabela conflitos com os novos dados estimados por ML
        conn_update = get_db_connection()
        cursor_update = conn_update.cursor()
        cursor_update.execute('''
            UPDATE conflitos
            SET previsao_fatalidades = ?, tendencia_previsao = ?
            WHERE id_conflito = ?
        ''', (previsao, tendencia, cid))
        conn_update.commit()
        conn_update.close()
        
        print(f"  -> [ML Model] Analisando {c['pais']} ({cid}): Previsão próximo mês: {previsao} | Tendência: {tendencia}")
    print("[ML] Atualização concluída com sucesso.")
