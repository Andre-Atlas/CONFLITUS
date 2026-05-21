# -*- coding: utf-8 -*-
from .conexao import get_db_connection

def inicializar_tabelas():
    """Cria a estrutura inicial do banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paises (
            nome TEXT PRIMARY KEY,
            latitude REAL,
            longitude REAL,
            em_conflito BOOLEAN DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fontes_dados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instituicao TEXT,
            url_documento TEXT,
            data_coleta TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zonas_risco (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pais_nome TEXT,
            latitude REAL,
            longitude REAL,
            raio_km REAL,
            nivel_risco TEXT,
            populacao_afetada INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conflitos (
            id_conflito TEXT PRIMARY KEY,
            iso3 TEXT,
            pais TEXT,
            latitude REAL,
            longitude REAL,
            raio_km REAL DEFAULT 200.0,
            nivel_risco TEXT DEFAULT 'Médio',
            causa_principal TEXT DEFAULT '',
            contexto_historico TEXT DEFAULT '',
            fatalidades_estimadas INTEGER DEFAULT 0,
            fonte_dados TEXT DEFAULT 'ACLED',
            data_atualizacao TEXT,
            previsao_fatalidades INTEGER DEFAULT 0,
            tendencia_previsao TEXT DEFAULT 'Estável'
        )
    ''')

    # Tenta adicionar as colunas de previsão se não existirem (migração dinâmica)
    try:
        cursor.execute("ALTER TABLE conflitos ADD COLUMN previsao_fatalidades INTEGER DEFAULT 0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE conflitos ADD COLUMN tendencia_previsao TEXT DEFAULT 'Estável'")
    except Exception:
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atores_conflito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_conflito TEXT,
            nome TEXT,
            tipo TEXT,
            FOREIGN KEY (id_conflito) REFERENCES conflitos(id_conflito)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dados_grafico_mensal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_conflito TEXT,
            mes TEXT,
            fatalidades INTEGER DEFAULT 0,
            FOREIGN KEY (id_conflito) REFERENCES conflitos(id_conflito)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos_conflito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_conflito TEXT,
            data TEXT,
            localizacao TEXT,
            detalhes TEXT,
            fatalidades INTEGER DEFAULT 0,
            tipo TEXT,
            FOREIGN KEY (id_conflito) REFERENCES conflitos(id_conflito)
        )
    ''')

    conn.commit()
    conn.close()

# =====================================================================
# Funções existentes (países, fontes, zonas de risco)
# =====================================================================

def inserir_pais(nome, lat, lon):
    """Salva um país vindo da API no banco."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO paises VALUES (?, ?, ?, ?)', (nome, lat, lon, 0))
    conn.commit()
    conn.close()

def buscar_fontes():
    """Recupera todas as fontes registradas."""
    conn = get_db_connection()
    cursor = conn.cursor()
    fontes = cursor.execute('SELECT * FROM fontes_dados').fetchall()
    conn.close()
    return fontes

def registrar_fonte(instituicao, url, data):
    """Salva uma nova fonte de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO fontes_dados (instituicao, url_documento, data_coleta) VALUES (?, ?, ?)', 
                   (instituicao, url, data))
    conn.commit()
    conn.close()

def buscar_coordenadas_pais(nome_pais):
    """Procura no banco a latitude e longitude de um país pelo nome."""
    conn = get_db_connection()
    cursor = conn.cursor()
    resultado = cursor.execute(
        'SELECT latitude, longitude FROM paises WHERE nome LIKE ?', 
        (f"%{nome_pais}%",)
    ).fetchone()
    conn.close()
    return resultado 

def buscar_todas_zonas_ativas():
    """Recupera todas as zonas de conflito registradas no banco."""
    conn = get_db_connection()
    cursor = conn.cursor()
    zonas = cursor.execute('SELECT latitude, longitude, raio_km, nivel_risco FROM zonas_risco').fetchall()
    conn.close()
    return zonas

def inserir_zona_risco(pais, lat, lon, raio_km, nivel_risco, populacao_afetada):
    """Salva uma nova zona de conflito baseada nos dados da ACLED."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO zonas_risco (pais_nome, latitude, longitude, raio_km, nivel_risco, populacao_afetada)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (pais, lat, lon, raio_km, nivel_risco, populacao_afetada))
    
    conn.commit()
    conn.close()

# =====================================================================
# Novas funções para conflitos educativos
# =====================================================================

def inserir_conflito(id_conflito, iso3, pais, lat, lon, raio_km, nivel_risco, causa, contexto, fatalidades, fonte, data_atualiz):
    """Insere ou atualiza um conflito no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO conflitos 
        (id_conflito, iso3, pais, latitude, longitude, raio_km, nivel_risco, causa_principal, contexto_historico, fatalidades_estimadas, fonte_dados, data_atualizacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id_conflito, iso3, pais, lat, lon, raio_km, nivel_risco, causa, contexto, fatalidades, fonte, data_atualiz))
    conn.commit()
    conn.close()

def inserir_ator(id_conflito, nome, tipo):
    """Insere um ator envolvido em um conflito."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO atores_conflito (id_conflito, nome, tipo) VALUES (?, ?, ?)', (id_conflito, nome, tipo))
    conn.commit()
    conn.close()

def inserir_dado_grafico(id_conflito, mes, fatalidades):
    """Insere um ponto de dado mensal para o gráfico de um conflito."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO dados_grafico_mensal (id_conflito, mes, fatalidades) VALUES (?, ?, ?)', (id_conflito, mes, fatalidades))
    conn.commit()
    conn.close()

def limpar_atores(id_conflito):
    """Remove todos os atores de um conflito (para re-inserção)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM atores_conflito WHERE id_conflito = ?', (id_conflito,))
    conn.commit()
    conn.close()

def limpar_dados_grafico(id_conflito):
    """Remove todos os dados de gráfico de um conflito (para re-inserção)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM dados_grafico_mensal WHERE id_conflito = ?', (id_conflito,))
    conn.commit()
    conn.close()

def inserir_evento_conflito(id_conflito, data, localizacao, detalhes, fatalidades, tipo):
    """Insere um evento pontual de conflito no banco de dados."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO eventos_conflito (id_conflito, data, localizacao, detalhes, fatalidades, tipo)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (id_conflito, data, localizacao, detalhes, fatalidades, tipo))
    conn.commit()
    conn.close()

def limpar_eventos_conflito(id_conflito):
    """Remove todos os eventos pontuais de um conflito."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM eventos_conflito WHERE id_conflito = ?', (id_conflito,))
    conn.commit()
    conn.close()

def tem_conflitos():
    """Verifica se existem conflitos cadastrados no banco."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        count = cursor.execute('SELECT COUNT(*) FROM conflitos').fetchone()[0]
        conn.close()
        return count > 0
    except:
        conn.close()
        return False

def buscar_todos_conflitos():
    """Retorna todos os conflitos formatados para o frontend."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    conflitos_raw = cursor.execute('SELECT * FROM conflitos ORDER BY fatalidades_estimadas DESC').fetchall()
    resultado = []
    
    for c in conflitos_raw:
        id_c = c['id_conflito']
        
        atores_raw = cursor.execute('SELECT nome, tipo FROM atores_conflito WHERE id_conflito = ?', (id_c,)).fetchall()
        atores = [{"nome": a["nome"], "tipo": a["tipo"]} for a in atores_raw]
        
        graf_raw = cursor.execute('SELECT mes, fatalidades FROM dados_grafico_mensal WHERE id_conflito = ? ORDER BY id', (id_c,)).fetchall()
        meses = [g["mes"] for g in graf_raw]
        fatalidades = [g["fatalidades"] for g in graf_raw]
        
        # Buscar eventos recentes
        eventos_raw = cursor.execute('''
            SELECT data, localizacao, detalhes, fatalidades, tipo 
            FROM eventos_conflito 
            WHERE id_conflito = ? 
            ORDER BY data DESC
        ''', (id_c,)).fetchall()
        eventos_recentes = [{
            "data": ev["data"],
            "localizacao": ev["localizacao"],
            "detalhes": ev["detalhes"],
            "fatalidades": ev["fatalidades"],
            "tipo": ev["tipo"]
        } for ev in eventos_raw]
        
        resultado.append({
            "id_conflito": c["id_conflito"],
            "iso3": c["iso3"],
            "pais": c["pais"],
            "latitude": c["latitude"],
            "longitude": c["longitude"],
            "raio_km": c["raio_km"],
            "nivel_risco": c["nivel_risco"],
            "causa_principal": c["causa_principal"],
            "contexto_historico": c["contexto_historico"],
            "atores": atores,
            "fatalidades_estimadas": c["fatalidades_estimadas"],
            "fonte_dados": c["fonte_dados"],
            "data_atualizacao": c["data_atualizacao"],
            "previsao_fatalidades": c["previsao_fatalidades"] if "previsao_fatalidades" in c.keys() else 0,
            "tendencia_previsao": c["tendencia_previsao"] if "tendencia_previsao" in c.keys() else "Estável",
            "dados_grafico": {
                "meses": meses if meses else ["Dez", "Jan", "Fev", "Mar", "Abr", "Mai"],
                "fatalidades": fatalidades if fatalidades else [0, 0, 0, 0, 0, 0]
            },
            "eventos_recentes": eventos_recentes
        })
    
    conn.close()
    return resultado