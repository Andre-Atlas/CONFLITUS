export interface AtorEnvolvido {
  nome: string;
  tipo: string;
}

export interface DadosGrafico {
  meses: string[];
  fatalidades: number[];
}

export interface EventoConflito {
  data: string;
  localizacao: string;
  detalhes: string;
  fatalidades: number;
  tipo: string;
}

export interface ConflitoEducativo {
  id_conflito: string;
  iso3: string;
  pais: string;
  latitude: number;
  longitude: number;
  raio_km: number;
  nivel_risco: "Baixo" | "Médio" | "Alto" | "Crítico";
  causa_principal: string;
  contexto_historico: string;
  atores: AtorEnvolvido[];
  fatalidades_estimadas: number;
  fonte_dados: string;
  data_atualizacao: string;
  dados_grafico: DadosGrafico;
  eventos_recentes?: EventoConflito[];
  previsao_fatalidades?: number;
  tendencia_previsao?: string;
}


export interface RotaAcolhimento {
  pais: string;
  destino_iata: string;
  disponivel: boolean;
  preco?: string;
  companhia_aerea?: string;
  duracao?: string;
  escalas?: number;
  mensagem?: string;
  destino_lat?: number;
  destino_lon?: number;
}
