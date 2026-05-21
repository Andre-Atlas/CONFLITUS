# -*- coding: utf-8 -*-
import requests
import os
from datetime import date, datetime, timedelta
from collections import defaultdict
import pandas as pd
from app.database import operacoes
from app.ml import atualizar_todas_previsoes
from dotenv import load_dotenv

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_env = os.path.join(diretorio_atual, "..", "..", ".env")

load_dotenv(dotenv_path=caminho_env)

# =====================================================================
# Mapeamento de países (inglês -> iso3, nome em português)
# =====================================================================

COUNTRY_MAP = {
    "Sudan": ("SDN", "Sudão"),
    "Myanmar": ("MMR", "Mianmar"),
    "Ukraine": ("UKR", "Ucrânia"),
    "Colombia": ("COL", "Colômbia"),
    "Syria": ("SYR", "Síria"),
    "Yemen": ("YEM", "Iêmen"),
    "Ethiopia": ("ETH", "Etiópia"),
    "Somalia": ("SOM", "Somália"),
    "Democratic Republic of Congo": ("COD", "Rep. Dem. Congo"),
    "Nigeria": ("NGA", "Nigéria"),
    "Mali": ("MLI", "Mali"),
    "Burkina Faso": ("BFA", "Burkina Faso"),
    "Mozambique": ("MOZ", "Moçambique"),
    "Afghanistan": ("AFG", "Afeganistão"),
    "Iraq": ("IRQ", "Iraque"),
    "Libya": ("LBY", "Líbia"),
    "Palestine": ("PSE", "Palestina"),
    "Israel": ("ISR", "Israel"),
    "Niger": ("NER", "Níger"),
    "Cameroon": ("CMR", "Camarões"),
    "Chad": ("TCD", "Chade"),
    "Central African Republic": ("CAF", "Rep. Centro-Africana"),
    "South Sudan": ("SSD", "Sudão do Sul"),
    "Mexico": ("MEX", "México"),
    "Philippines": ("PHL", "Filipinas"),
    "India": ("IND", "Índia"),
    "Pakistan": ("PAK", "Paquistão"),
    "Thailand": ("THA", "Tailândia"),
}

# =====================================================================
# Dados seed editoriais (espelho do server.ts)
# =====================================================================

SEED_DATA = [
    {
        "id_conflito": "SUD-2023",
        "iso3": "SDN",
        "pais": "Sudão",
        "latitude": 15.5007,
        "longitude": 32.5599,
        "raio_km": 800.0,
        "nivel_risco": "Crítico",
        "causa_principal": "Disputa de poder entre as Forças Armadas e milícias paramilitares organizadas.",
        "contexto_historico": "A escalada de violência que teve início em 2023 surge do colapso no processo de transição civil após a deposição do antigo regime em 2019. Tensão sob recursos hídricos, controle de rotas de mineração e apropriação do aparato militar culminaram numa disputa aberta.",
        "atores": [
            {"nome": "Forças Armadas do Sudão (SAF)", "tipo": "Governo/Militar"},
            {"nome": "Forças de Apoio Rápido (RSF)", "tipo": "Força Paramilitar"},
        ],
        "fatalidades_estimadas": 15400,
        "fonte_dados": "UCDP e ACLED",
        "data_atualizacao": "2026-05-18",
        "dados_grafico": {
            "meses": ["Dez", "Jan", "Fev", "Mar", "Abr", "Mai"],
            "fatalidades": [500, 1200, 3000, 4500, 3800, 2400],
        },
    },
    {
        "id_conflito": "MYA-2021",
        "iso3": "MMR",
        "pais": "Mianmar",
        "latitude": 21.9162,
        "longitude": 95.9560,
        "raio_km": 600.0,
        "nivel_risco": "Alto",
        "causa_principal": "Golpe militar e guerra civil com alianças étnicas.",
        "contexto_historico": "Após as forças armadas deporem o governo democraticamente eleito, grupos de resistência armada se organizaram ao lado das históricas organizações étnicas, unificando os protestos contra o regime militar instaurado desde o dia do golpe.",
        "atores": [
            {"nome": "Forças Armadas (Tatmadaw)", "tipo": "Regime Militar"},
            {"nome": "Forças de Defesa Popular (PDF)", "tipo": "Resistência Armada"},
            {"nome": "Aliança das Três Irmandades", "tipo": "Organização Étnica Rebelde"},
        ],
        "fatalidades_estimadas": 9300,
        "fonte_dados": "UCDP e ACLED",
        "data_atualizacao": "2026-05-15",
        "dados_grafico": {
            "meses": ["Dez", "Jan", "Fev", "Mar", "Abr", "Mai"],
            "fatalidades": [400, 800, 1500, 1800, 2600, 2200],
        },
    },
    {
        "id_conflito": "UKR-2022",
        "iso3": "UKR",
        "pais": "Ucrânia",
        "latitude": 49.3331,
        "longitude": 37.3621,
        "raio_km": 1200.0,
        "nivel_risco": "Crítico",
        "causa_principal": "Invasão militar e disputa territorial escalada.",
        "contexto_historico": "Um conflito armado que se iniciou logo após movimentos de mudança política e disputas na península da Crimeia e na região de Donbas. O conflito evoluiu gravemente com uma escalada em larga escala por intervenção em territórios soberanos.",
        "atores": [
            {"nome": "Forças Armadas", "tipo": "Militar Nacional"},
            {"nome": "Milícias e Voluntários", "tipo": "Forças Irregulares"},
            {"nome": "Intervenção Estrangeira", "tipo": "Estado Invasor/Aliados"},
        ],
        "fatalidades_estimadas": 85000,
        "fonte_dados": "UCDP",
        "data_atualizacao": "2026-05-12",
        "dados_grafico": {
            "meses": ["Dez", "Jan", "Fev", "Mar", "Abr", "Mai"],
            "fatalidades": [12000, 15000, 14000, 16000, 18000, 10000],
        },
    },
    {
        "id_conflito": "COL-1964",
        "iso3": "COL",
        "pais": "Colômbia",
        "latitude": 3.5298,
        "longitude": -71.5037,
        "raio_km": 500.0,
        "nivel_risco": "Médio",
        "causa_principal": "Disputas paramilitares e narcotráfico residual.",
        "contexto_historico": "Mesmo historicamente sendo o teatro de uma guerra civil antiga, o atual cenário se concentra na luta de grupos dissidentes que não assinaram o tratado de paz de 2016 e estão conectados a ramificações com as rotas de drogas ilícitas.",
        "atores": [
            {"nome": "Governo Nacional", "tipo": "Estado"},
            {"nome": "Forças Dissidentes (ex-guerrilhas)", "tipo": "Grupo Armado Irregular"},
            {"nome": "Clãs do Narcotráfico", "tipo": "Organização Criminosa"},
        ],
        "fatalidades_estimadas": 1200,
        "fonte_dados": "Relatórios Locais e ACLED",
        "data_atualizacao": "2026-05-01",
        "dados_grafico": {
            "meses": ["Dez", "Jan", "Fev", "Mar", "Abr", "Mai"],
            "fatalidades": [150, 180, 200, 190, 250, 230],
        },
    },
]

CURATED_PROFILES = {
    "SYR": {
        "causa_principal": "Guerra civil de longa duração envolvendo forças governamentais, rebeldes da oposição e coalizões internacionais.",
        "contexto_historico": "Iniciada em 2011 durante a Primavera Árabe, a crise na Síria evoluiu de protestos pacíficos para um conflito militarizado complexo que fragmentou o controle do território nacional e desencadeou uma das maiores crises humanitárias do século XXI.",
        "atores": [
            {"nome": "Forças Armadas da Síria", "tipo": "Exército Governamental"},
            {"nome": "Força de Defesa Nacional", "tipo": "Milícia Pró-Governo"},
            {"nome": "Forças Democráticas Sírias (SDF)", "tipo": "Aliança Liderada por Curdos"},
            {"nome": "Grupos de Oposição Síria (SNA)", "tipo": "Resistência Armada"}
        ]
    },
    "YEM": {
        "causa_principal": "Conflito de poder entre o governo oficialmente reconhecido e o movimento rebelde Houthi.",
        "contexto_historico": "A guerra civil escalou em 2015 com a intervenção militar de uma coalizão liderada pela Arábia Saudita em apoio ao governo de transição. O país enfrenta uma crise alimentar crônica severa e instabilidade territorial com controle repartido.",
        "atores": [
            {"nome": "Movimento Ansar Allah (Houthis)", "tipo": "Grupo Rebelde Armado"},
            {"nome": "Forças Governamentais do Iêmen", "tipo": "Exército Oficial"},
            {"nome": "Conselho de Transição do Sul (STC)", "tipo": "Movimento Separatista"},
            {"nome": "Coalizão Liderada pela Arábia Saudita", "tipo": "Intervenção Externa"}
        ]
    },
    "SOM": {
        "causa_principal": "Insurreição fundamentalista islâmica e disputa por controle territorial.",
        "contexto_historico": "O grupo extremista Al-Shabaab iniciou sua insurgência armada há quase duas décadas com o objetivo de derrubar o governo federal somali. Operações antiterrorismo do exército oficial em conjunto com clãs locais e forças de paz da União Africana marcam o conflito.",
        "atores": [
            {"nome": "Forças de Segurança da Somália", "tipo": "Força Estatal"},
            {"nome": "Harakat al-Shabaab al-Mujahideen", "tipo": "Grupo Insurgente Extremista"},
            {"nome": "Missão de Transição da União Africana (ATMIS)", "tipo": "Força de Paz Regional"},
            {"nome": "Milícias de Clãs Locais (Macawisley)", "tipo": "Grupo de Autodefesa"}
        ]
    },
    "NGA": {
        "causa_principal": "Insurgência jihadista no nordeste e confrontos intercomunitários de bandidagem no noroeste.",
        "contexto_historico": "Desde 2009, o grupo Boko Haram e posteriormente o braço dissidente ISWAP espalham violência no nordeste nigeriano. Paralelamente, disputas históricas por pasto e recursos entre pastores nómades Fulani e agricultores locais escalaram para ataques sistemáticos por bandos armados.",
        "atores": [
            {"nome": "Forças Armadas da Nigéria", "tipo": "Militar Nacional"},
            {"nome": "Boko Haram (JAS)", "tipo": "Grupo Insurgente Extremista"},
            {"nome": "Estado Islâmico na Província da África Ocidental (ISWAP)", "tipo": "Grupo Extremista Dissidente"},
            {"nome": "Milícias de Bandidos Armados", "tipo": "Organização Criminosa/Irregular"}
        ]
    },
    "ETH": {
        "causa_principal": "Tensões étnicas e disputas de fronteiras subnacionais por autonomia política.",
        "contexto_historico": "Após o acordo que encerrou a guerra na região do Tigré em 2022, tensões militares deslocaram-se para as províncias vizinhas de Amhara e Oromia. Confrontos ocorrem entre tropas estatais e milícias locais que se recusam a desarmar.",
        "atores": [
            {"nome": "Força de Defesa Nacional da Etiópia (ENDF)", "tipo": "Militar Nacional"},
            {"nome": "Milícias Populares Amhara (Fano)", "tipo": "Força Irregular Regional"},
            {"nome": "Exército de Libertação Oromo (OLA)", "tipo": "Grupo Rebelde Étnico"}
        ]
    },
    "PAK": {
        "causa_principal": "Insurgência de movimentos islâmicos fundamentalistas e separatistas regionais.",
        "contexto_historico": "O exército paquistanês combate o grupo insurgente Tehrik-i-Taliban Pakistan (TTP) ao longo da fronteira com o Afeganistão. Além disso, a região rica em recursos do Baluchistão enfrenta insurgência histórica de grupos nacionalistas que exigem independência total.",
        "atores": [
            {"nome": "Forças Armadas do Paquistão", "tipo": "Exército Nacional"},
            {"nome": "Tehrik-i-Taliban Pakistan (TTP)", "tipo": "Movimento Fundamentalista Insurgente"},
            {"nome": "Exército de Libertação do Baluchistão (BLA)", "tipo": "Grupo Rebelde Separatista"}
        ]
    },
    "IND": {
        "causa_principal": "Insurgência maoísta residual e conflitos de fronteira contestada na Caxemira.",
        "contexto_historico": "A Índia enfrenta insurgências maoístas de longa duração (Naxalitas) no centro-leste, ao mesmo tempo em que tropas de segurança combatem grupos infiltrados e separatistas na região de Jammu e Caxemira, sob constante tensionamento militar de fronteiras.",
        "atores": [
            {"nome": "Forças de Segurança da Índia (CRPF)", "tipo": "Força Militar/Policial"},
            {"nome": "Exército de Libertação do Povo Guerrilheiro (PLGA/Naxalitas)", "tipo": "Grupo Rebelde Maoísta"},
            {"nome": "Lashkar-e-Taiba / Jaish-e-Mohammed", "tipo": "Células Militantes na Caxemira"}
        ]
    },
    "IRQ": {
        "causa_principal": "Instabilidade residual pós-Estado Islâmico e atividade de milícias sectárias.",
        "contexto_historico": "Apesar da declaração de vitória militar sobre o ISIS em 2017, células adormecidas continuam a realizar atentados no norte e oeste. Paralelamente, disputas de controle geopolítico envolvem milícias integradas ao aparato de segurança pública e facções locais.",
        "atores": [
            {"nome": "Forças de Segurança do Iraque", "tipo": "Exército Nacional"},
            {"nome": "Unidades de Mobilização Popular (PMF)", "tipo": "Unidades Militantes Aliadas"},
            {"nome": "Células Remanescentes do Estado Islâmico (ISIS)", "tipo": "Grupo Extremista Subterrâneo"},
            {"nome": "Peshmerga Curdo", "tipo": "Força de Segurança Regional"}
        ]
    },
    "MLI": {
        "causa_principal": "Insurgência armada jihadista associada à al-Qaeda e instabilidade após sucessivos golpes militares.",
        "contexto_historico": "O norte e centro do país sofrem com ações violentas de grupos extremistas móveis desde 2012. Após a retirada das missões de paz francesas e da ONU (MINUSMA), o governo militar aliado a assessores de segurança estrangeiros assumiu as ofensivas.",
        "atores": [
            {"nome": "Forças Armadas de Mali (FAMA)", "tipo": "Governo Militar"},
            {"nome": "Grupo de Apoio ao Islã e aos Muçulmanos (JNIM)", "tipo": "Aliança Jihadista al-Qaeda"},
            {"nome": "Coordenação dos Movimentos do Azawad (CMA)", "tipo": "Rebeldes Tuaregues Separatistas"}
        ]
    },
    "PSE": {
        "causa_principal": "Conflito territorial de longa data e ofensivas de segurança em larga escala.",
        "contexto_historico": "A crise humanitária nos territórios palestinos escalou de forma drástica com cercos militares, bloqueios estruturais e operações urbanas intensas no contexto de disputas históricas de soberania e autodeterminação.",
        "atores": [
            {"nome": "Forças de Segurança Local / Brigadas de Resistência", "tipo": "Grupos Armados Organizados"},
            {"nome": "Autoridade Palestina (Forças de Segurança)", "tipo": "Segurança Administrativa"}
        ]
    },
    "ISR": {
        "causa_principal": "Disputa territorial e ameaças à segurança de fronteiras nacionais.",
        "contexto_historico": "Estado caracterizado por alta militarização e defesa ativa de suas fronteiras soberanas no Oriente Médio. Enfrenta constantes trocas de fogo de artilharia e mísseis com grupos localizados em territórios vizinhos.",
        "atores": [
            {"nome": "Forças de Defesa de Israel (IDF)", "tipo": "Exército Nacional"},
            {"nome": "Serviços de Inteligência e Defesa Aérea", "tipo": "Forças Governamentais Especiais"}
        ]
    },
    "COD": {
        "causa_principal": "Combate contra grupos rebeldes armados no leste do país e controle de jazidas minerais.",
        "contexto_historico": "A província de Kivu do Norte e adjacências são palco de combates contínuos entre o exército governamental e o grupo rebelde M23. O conflito é agravado pela disputa da extração ilegal de cobalto, ouro e coltan.",
        "atores": [
            {"nome": "Forças Armadas da Rep. Dem. do Congo (FARDC)", "tipo": "Exército Governamental"},
            {"nome": "Movimento 23 de Março (M23)", "tipo": "Grupo Rebelde Armado"},
            {"nome": "Forças Democráticas Aliadas (ADF)", "tipo": "Grupo Fundamentalista Insurgente"}
        ]
    },
    "AFG": {
        "causa_principal": "Insurgência islâmica contra a província local e combate a facções rivais.",
        "contexto_historico": "Após a mudança radical de regime em 2021, o atual governo enfrenta forte oposição violenta de facções ainda mais radicais (como o ISKP) que conduzem ataques e atentados urbanos frequentes.",
        "atores": [
            {"nome": "Forças de Segurança do Governo Local", "tipo": "Força Regente de Fato"},
            {"nome": "Estado Islâmico da Província de Khorasan (ISKP)", "tipo": "Célula Extremista Rival"}
        ]
    }
}


class AcledService:
    def __init__(self):
        self.email = os.getenv("ACLED_EMAIL", "")
        self.password = os.getenv("ACLED_PASSWORD", os.getenv("ACLED_KEY", ""))
        self.token_url = "https://acleddata.com/oauth/token"
        self.base_url = "https://acleddata.com/api/acled/read"
        self._access_token = None

    def obter_token_acesso(self):
        if not self.email or not self.password:
            print("  -> Aviso: Credenciais ACLED_EMAIL ou ACLED_PASSWORD não encontradas no .env")
            return None

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "username": self.email,
            "password": self.password,
            "grant_type": "password",
            "client_id": "acled",
            "scope": "authenticated"
        }

        try:
            resp = requests.post(self.token_url, headers=headers, data=payload, timeout=15)
            resp.raise_for_status()
            self._access_token = resp.json().get("access_token")
            return self._access_token
        except Exception as e:
            print(f"  -> [Erro ACLED OAuth] Falha ao obter token: {e}")
            return None

    def buscar_conflitos(self, limit=5000):
        token = self._access_token or self.obter_token_acesso()
        if not token:
            return []

        hoje = date.today()
        seis_meses = hoje - timedelta(days=180)
        date_range = f"{seis_meses.isoformat()}|{hoje.isoformat()}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        params = {
            "_format": "json",
            "limit": limit,
            "event_type": "Battles",
            "event_date": date_range,
            "event_date_where": "between"
        }

        try:
            print("  -> Buscando eventos na ACLED usando OAuth Bearer Token...")
            resp = requests.get(self.base_url, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            dados = resp.json()
            data_list = dados.get("data", [])
            if data_list:
                return data_list
            
            # Força o fallback se a API retornar 200 OK mas com array vazio
            # (Comum em contas grátis devido a restrições de histórico)
            raise ValueError("API retornou sucesso, mas sem dados (restrição de tier). Tentando fallback...")
            
        except Exception as e:
            print(f"  -> [Erro ACLED Busca] Falha na requisição: {e}")
            # Tentar fallback sem data filter
            params.pop("event_date", None)
            params.pop("event_date_where", None)
            try:
                print("  -> Tentativa fallback (sem filtro de datas)...")
                resp = requests.get(self.base_url, headers=headers, params=params, timeout=30)
                resp.raise_for_status()
                dados = resp.json()
                if dados.get("data"):
                    return dados["data"]
            except Exception as e2:
                print(f"  -> [Erro ACLED Fallback] Falha na requisição: {e2}")
            return []


class PipelineDeDados:
    def __init__(self):
        operacoes.inicializar_tabelas()
        self.url_paises = "https://restcountries.com/v3.1/all"
        self.acled_service = AcledService()
        self.ucdp_token = os.getenv("UCDP_TOKEN", "")

    # =================================================================
    # Seed Data — dados editoriais base
    # =================================================================

    def carregar_seed_data(self):
        """Insere os 4 conflitos editoriais base no banco de dados."""
        print("[Pipeline] Carregando dados seed...")

        for conflito in SEED_DATA:
            cid = conflito["id_conflito"]

            # Insere o conflito principal
            operacoes.inserir_conflito(
                id_conflito=cid,
                iso3=conflito["iso3"],
                pais=conflito["pais"],
                lat=conflito["latitude"],
                lon=conflito["longitude"],
                raio_km=conflito["raio_km"],
                nivel_risco=conflito["nivel_risco"],
                causa=conflito["causa_principal"],
                contexto=conflito["contexto_historico"],
                fatalidades=conflito["fatalidades_estimadas"],
                fonte=conflito["fonte_dados"],
                data_atualiz=conflito["data_atualizacao"],
            )

            # Limpa e re-insere atores
            operacoes.limpar_atores(cid)
            for ator in conflito["atores"]:
                operacoes.inserir_ator(cid, ator["nome"], ator["tipo"])

            # Limpa e re-insere dados do gráfico
            operacoes.limpar_dados_grafico(cid)
            grafico = conflito["dados_grafico"]
            for mes, fat in zip(grafico["meses"], grafico["fatalidades"]):
                operacoes.inserir_dado_grafico(cid, mes, fat)

            print(f"  -> Conflito '{cid}' ({conflito['pais']}) inserido.")

        # Executa as previsões e tendências via ML para os dados seed
        atualizar_todas_previsoes()
        print(f"[Pipeline] {len(SEED_DATA)} conflitos seed carregados com sucesso!")

    # =================================================================
    # Enriquecimento via ACLED
    # =================================================================

    def enriquecer_com_acled(self):
        """Busca dados da ACLED API e enriquece os conflitos existentes utilizando Pandas."""
        print("\n[Pipeline] Iniciando enriquecimento via ACLED...")

        eventos = self.acled_service.buscar_conflitos()
        if not eventos:
            print("  -> Nenhum evento ACLED obtido. Pulando enriquecimento.")
            return

        # Carrega eventos no Pandas DataFrame
        df = pd.DataFrame(eventos)
        df['fatalities'] = pd.to_numeric(df['fatalities'], errors='coerce').fillna(0).astype(int)
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce').fillna(0.0)
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce').fillna(0.0)
        df['event_date_dt'] = pd.to_datetime(df['event_date'], format='%Y-%m-%d', errors='coerce')
        df['mes_label'] = df['event_date_dt'].dt.strftime('%b')

        print(f"  -> {len(eventos)} eventos carregados no Pandas DataFrame.")

        # Mapa de conflitos seed por iso3
        seed_iso3 = {s["iso3"]: s for s in SEED_DATA}
        hoje = date.today().isoformat()

        for country_en, info in COUNTRY_MAP.items():
            df_country = df[df['country'] == country_en]
            if df_country.empty:
                continue

            iso3, pais_pt = info
            total_fat = int(df_country['fatalities'].sum())

            # Extrai atores únicos (actor1 e actor2)
            atores = pd.concat([df_country['actor1'], df_country['actor2']]).dropna().unique()
            atores_set = {str(ator) for ator in atores if isinstance(ator, str) and len(ator) > 2}

            # Calcula dados mensais das fatalidades
            df_mensal = df_country.dropna(subset=['event_date_dt']).groupby('mes_label')['fatalities'].sum()
            mensal = df_mensal.to_dict()

            # Ordenar eventos para salvar os 5 mais recentes
            df_top_5 = df_country.sort_values(by='event_date', ascending=False).head(5)
            top_5_events = df_top_5.to_dict(orient='records')

            if iso3 in seed_iso3:
                # Atualiza conflito existente — adiciona fatalidades ACLED
                existente = seed_iso3[iso3]
                cid = existente["id_conflito"]

                novo_total = existente["fatalidades_estimadas"] + total_fat
                operacoes.inserir_conflito(
                    id_conflito=cid,
                    iso3=iso3,
                    pais=existente["pais"],
                    lat=existente["latitude"],
                    lon=existente["longitude"],
                    raio_km=existente["raio_km"],
                    nivel_risco=existente["nivel_risco"],
                    causa=existente["causa_principal"],
                    contexto=existente["contexto_historico"],
                    fatalidades=novo_total,
                    fonte=existente["fonte_dados"],
                    data_atualiz=hoje,
                )

                # Atualiza atores — adiciona os novos da ACLED
                for ator_nome in list(atores_set)[:5]:
                    operacoes.inserir_ator(cid, ator_nome, "Identificado via ACLED")

                # Salvar eventos recentes do conflito seed
                operacoes.limpar_eventos_conflito(cid)
                for ev in top_5_events:
                    data_ev = ev.get("event_date", "")
                    localizacao = f"{ev.get('location', '')}, {ev.get('admin1', '')}"
                    detalhes = ev.get("notes", "Sem detalhes adicionais.")
                    fatalidades_ev = int(ev.get("fatalities", 0))
                    tipo_ev = ev.get("event_type", "Combate")
                    operacoes.inserir_evento_conflito(cid, data_ev, localizacao, detalhes, fatalidades_ev, tipo_ev)

                print(f"  -> Atualizado: {pais_pt} ({cid}) — +{total_fat} fatalidades ACLED e feed de eventos criado")

            elif total_fat > 50:
                # Novo conflito significativo
                cid = f"{iso3}-ACLED"
                lat_media = float(df_country['latitude'].mean())
                lon_media = float(df_country['longitude'].mean())

                nivel = "Crítico" if total_fat > 500 else "Alto" if total_fat > 100 else "Médio"

                # Busca perfil curado se existir
                profile = CURATED_PROFILES.get(iso3)
                if profile:
                    causa = profile["causa_principal"]
                    contexto = profile["contexto_historico"] + f" Total de {total_fat} fatalidades registradas nos últimos 6 meses (Fonte: ACLED)."
                else:
                    causa = f"Eventos de conflito armado identificados via ACLED ({len(df_country)} eventos)."
                    contexto = f"Dados coletados automaticamente da ACLED. Total de {total_fat} fatalidades registradas nos últimos 6 meses."

                operacoes.inserir_conflito(
                    id_conflito=cid,
                    iso3=iso3,
                    pais=pais_pt,
                    lat=lat_media,
                    lon=lon_media,
                    raio_km=200.0,
                    nivel_risco=nivel,
                    causa=causa,
                    contexto=contexto,
                    fatalidades=total_fat,
                    fonte="ACLED",
                    data_atualiz=hoje,
                )

                # Limpa e reinsere atores
                operacoes.limpar_atores(cid)
                inseridos_nomes = set()
                if profile and "atores" in profile:
                    for ator in profile["atores"]:
                        operacoes.inserir_ator(cid, ator["nome"], ator["tipo"])
                        inseridos_nomes.add(ator["nome"])

                # Completa com atores identificados pela ACLED
                for ator_nome in list(atores_set):
                    if len(inseridos_nomes) >= 5:
                        break
                    if ator_nome not in inseridos_nomes:
                        operacoes.inserir_ator(cid, ator_nome, "Identificado via ACLED")
                        inseridos_nomes.add(ator_nome)

                # Limpa e reinsere dados do gráfico
                operacoes.limpar_dados_grafico(cid)
                if mensal:
                    for mes_k, fat_v in mensal.items():
                        operacoes.inserir_dado_grafico(cid, mes_k, fat_v)

                # Salvar eventos recentes do novo conflito
                operacoes.limpar_eventos_conflito(cid)
                for ev in top_5_events:
                    data_ev = ev.get("event_date", "")
                    localizacao = f"{ev.get('location', '')}, {ev.get('admin1', '')}"
                    detalhes = ev.get("notes", "Sem detalhes adicionais.")
                    fatalidades_ev = int(ev.get("fatalities", 0))
                    tipo_ev = ev.get("event_type", "Combate")
                    operacoes.inserir_evento_conflito(cid, data_ev, localizacao, detalhes, fatalidades_ev, tipo_ev)

                print(f"  -> Novo conflito: {pais_pt} ({cid}) — {total_fat} fatalidades e feed de eventos criado")

        print("[Pipeline] Enriquecimento ACLED concluído.")

    # Método original _buscar_eventos_acled foi substituído por AcledService

    # =================================================================
    # Enriquecimento via UCDP
    # =================================================================

    def enriquecer_com_ucdp(self):
        """Busca dados do UCDP GED API e enriquece os conflitos utilizando Pandas."""
        print("\n[Pipeline] Iniciando enriquecimento via UCDP...")

        try:
            url = "https://ucdpapi.pcr.uu.se/api/gedevents/24.0.12?pagesize=100"
            headers = {"Accept": "application/json"}

            if self.ucdp_token:
                headers["Authorization"] = f"Bearer {self.ucdp_token}"

            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            results = data.get("Result", [])
            if not results:
                print("  -> Nenhum evento UCDP obtido.")
                return

            # Carrega no Pandas DataFrame
            df = pd.DataFrame(results)
            df['best'] = pd.to_numeric(df['best'], errors='coerce').fillna(0).astype(int)
            df['low'] = pd.to_numeric(df['low'], errors='coerce').fillna(0).astype(int)
            df['high'] = pd.to_numeric(df['high'], errors='coerce').fillna(0).astype(int)
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce').fillna(0.0)
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce').fillna(0.0)

            # Calcula a melhor estimativa de fatalidade
            df['fat_calc'] = df.apply(lambda r: r['best'] if r['best'] > 0 else int((r['low'] + r['high']) / 2), axis=1)

            print(f"  -> {len(results)} eventos UCDP carregados no Pandas DataFrame.")

            # Mapa de conflitos seed por iso3
            seed_iso3 = {s["iso3"]: s for s in SEED_DATA}
            hoje = date.today().isoformat()

            for country_en, info in COUNTRY_MAP.items():
                df_country = df[df['country'] == country_en]
                if df_country.empty:
                    continue

                iso3, pais_pt = info
                total_fat = int(df_country['fat_calc'].sum())
                if total_fat == 0:
                    continue

                if iso3 in seed_iso3:
                    existente = seed_iso3[iso3]
                    cid = existente["id_conflito"]

                    # Apenas atualiza fatalidades se UCDP trouxe dados significativos
                    novo_total = existente["fatalidades_estimadas"] + total_fat
                    operacoes.inserir_conflito(
                        id_conflito=cid,
                        iso3=iso3,
                        pais=existente["pais"],
                        lat=existente["latitude"],
                        lon=existente["longitude"],
                        raio_km=existente["raio_km"],
                        nivel_risco=existente["nivel_risco"],
                        causa=existente["causa_principal"],
                        contexto=existente["contexto_historico"],
                        fatalidades=novo_total,
                        fonte=existente["fonte_dados"],
                        data_atualiz=hoje,
                    )
                    print(f"  -> Atualizado via UCDP: {pais_pt} — +{total_fat} fatalidades")

                elif total_fat > 50:
                    cid = f"{iso3}-UCDP"
                    lat_media = float(df_country['latitude'].mean())
                    lon_media = float(df_country['longitude'].mean())

                    nivel = "Crítico" if total_fat > 500 else "Alto" if total_fat > 100 else "Médio"

                    operacoes.inserir_conflito(
                        id_conflito=cid,
                        iso3=iso3,
                        pais=pais_pt,
                        lat=lat_media,
                        lon=lon_media,
                        raio_km=200.0,
                        nivel_risco=nivel,
                        causa=f"Eventos de conflito identificados via UCDP ({len(df_country)} registros).",
                        contexto=f"Dados coletados automaticamente do UCDP GED. Total de {total_fat} fatalidades estimadas.",
                        fatalidades=total_fat,
                        fonte="UCDP",
                        data_atualiz=hoje,
                    )

                    operacoes.limpar_atores(cid)
                    # UCDP tem side_a e side_b
                    atores = pd.concat([df_country['side_a'], df_country['side_b']]).dropna().unique()
                    atores_set = {str(ator) for ator in atores if isinstance(ator, str) and len(ator) > 2}
                    for ator_nome in list(atores_set)[:5]:
                        operacoes.inserir_ator(cid, ator_nome, "Identificado via UCDP")

                    print(f"  -> Novo conflito UCDP: {pais_pt} ({cid}) — {total_fat} fatalidades")

            print("[Pipeline] Enriquecimento UCDP concluído.")

        except requests.exceptions.HTTPError as e:
            print(f"  -> Erro HTTP na UCDP: {e.response.status_code if e.response else 'N/A'}")
        except requests.exceptions.ConnectionError:
            print("  -> Erro de conexão com UCDP. Serviço pode estar indisponível.")
        except requests.exceptions.Timeout:
            print("  -> Timeout na conexão com UCDP.")
        except Exception as e:
            print(f"  -> Erro inesperado no UCDP: {e}")

    # =================================================================
    # Carga de países (geográfica) — preservado do original
    # =================================================================

    def executar_carga_paises(self):
        """Busca dados geográficos de países via APIs públicas."""
        print("\n[Pipeline] Iniciando carga de dados geográficos...")

        url_primaria = "https://restcountries.com/v3.1/all?fields=name,latlng"
        cabecalhos = {"User-Agent": "Mozilla/5.0"}

        try:
            print("  -> Tentando conectar à API Primária (restcountries)...")
            resposta = requests.get(url_primaria, headers=cabecalhos, timeout=10)
            resposta.raise_for_status()

            paises = resposta.json()
            paises_inseridos = 0

            for p in paises:
                nome = p.get('name', {}).get('common')
                latlng = p.get('latlng', [])
                if nome and len(latlng) == 2:
                    operacoes.inserir_pais(nome, latlng[0], latlng[1])
                    paises_inseridos += 1

            print(f"  -> Sucesso! {paises_inseridos} países salvos no SQLite.")
            return

        except Exception as e:
            print(f"  -> API Primária falhou ({e}). Ativando failover...")

        url_secundaria = "https://countriesnow.space/api/v0.1/countries/positions"

        try:
            resposta = requests.get(url_secundaria, timeout=10)
            resposta.raise_for_status()

            dados_json = resposta.json()
            paises = dados_json.get('data', [])

            paises_inseridos = 0
            for p in paises:
                nome = p.get('name')
                lat = p.get('lat')
                lon = p.get('long')

                if nome and lat is not None and lon is not None:
                    operacoes.inserir_pais(nome, float(lat), float(lon))
                    paises_inseridos += 1

            print(f"  -> Sucesso na API Secundária! {paises_inseridos} países salvos.")

        except Exception as e:
            print(f"  -> API Secundária também falhou: {e}")

    # =================================================================
    # Execução completa do pipeline
    # =================================================================

    def executar_carga_completa(self):
        """Executa o pipeline completo: seed → ACLED → UCDP."""
        print("=" * 60)
        print("  CONFLITUS — Pipeline de Dados Geopolíticos")
        print("=" * 60)

        # Etapa 1: Dados seed editoriais
        try:
            self.carregar_seed_data()
        except Exception as e:
            print(f"[ERRO] Falha ao carregar seed data: {e}")

        # Etapa 2: Enriquecimento ACLED
        try:
            self.enriquecer_com_acled()
        except Exception as e:
            print(f"[ERRO] Falha no enriquecimento ACLED: {e}")

        # Etapa 3: Enriquecimento UCDP
        try:
            self.enriquecer_com_ucdp()
        except Exception as e:
            print(f"[ERRO] Falha no enriquecimento UCDP: {e}")

        # Atualiza previsões e tendências via Scikit-Learn ML
        try:
            atualizar_todas_previsoes()
        except Exception as e:
            print(f"[ERRO] Falha ao atualizar previsões via ML: {e}")

        print("\n" + "=" * 60)
        print("  Pipeline concluído!")
        print("=" * 60)


# --- Execução direta do Pipeline ---
if __name__ == "__main__":
    p = PipelineDeDados()
    p.executar_carga_completa()