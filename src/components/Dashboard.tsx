import React from 'react';
import { ConflitoEducativo } from '../types';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Globe2, ShieldAlert, ArrowLeft, Users, FileText, Filter, Search, ChevronRight, Clock, Calendar } from 'lucide-react';
import RotasDeAcolhimento from './RotasDeAcolhimento';

interface DashboardProps {
  conflitos: ConflitoEducativo[];
  selectedConflito: ConflitoEducativo | null;
  onBack: () => void;
  riscoFilter: string;
  onFilterChange: (risco: string) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onSelect: (c: ConflitoEducativo) => void;
  onHover: (c: ConflitoEducativo | null) => void;
  onRoutesLoaded: (rotas: any[]) => void;
}

export default function Dashboard({ conflitos, selectedConflito, onBack, riscoFilter, onFilterChange, searchQuery, onSearchChange, onSelect, onHover, onRoutesLoaded }: DashboardProps) {
  if (selectedConflito) {
    return <DetailDashboard conflito={selectedConflito} onBack={onBack} onRoutesLoaded={onRoutesLoaded} />;
  }
  return <GlobalDashboard conflitos={conflitos} riscoFilter={riscoFilter} onFilterChange={onFilterChange} searchQuery={searchQuery} onSearchChange={onSearchChange} onSelect={onSelect} onHover={onHover} />;
}

function GlobalDashboard({ conflitos, riscoFilter, onFilterChange, searchQuery, onSearchChange, onSelect, onHover }: { conflitos: ConflitoEducativo[], riscoFilter: string, onFilterChange: (r: string) => void, searchQuery: string, onSearchChange: (q: string) => void, onSelect: (c: ConflitoEducativo) => void, onHover: (c: ConflitoEducativo | null) => void }) {
  const totalConflitos = conflitos.length;
  const totalMortes = conflitos.reduce((acc, curr) => acc + curr.fatalidades_estimadas, 0);

  const filterOptions = ["Todos", "Crítico", "Alto", "Médio", "Baixo"];

  const getRiskColor = (risco: string) => {
    return {
      "Crítico": "bg-rose-500/20 text-rose-400 border-rose-500/30",
      "Alto": "bg-orange-500/20 text-orange-400 border-orange-500/30",
      "Médio": "bg-amber-500/20 text-amber-400 border-amber-500/30",
      "Baixo": "bg-slate-500/20 text-slate-400 border-slate-500/30"
    }[risco] || "bg-slate-600/20 text-slate-400";
  };

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-800 shrink-0">
        <Globe2 className="w-8 h-8 text-rose-500" />
        <h1 className="text-2xl font-semibold tracking-tight text-white">Observatório Geopolítico</h1>
      </div>

      <div className="mb-6 space-y-5 shrink-0">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-slate-400" />
          </div>
          <input
            type="text"
            placeholder="Pesquisar por país..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-slate-700/80 rounded-md leading-5 bg-slate-800/40 text-slate-300 placeholder-slate-500 focus:outline-none focus:bg-slate-800 focus:border-rose-500/50 focus:ring-1 focus:ring-rose-500/50 sm:text-sm transition-colors"
          />
        </div>

        <div>
          <div className="flex flex-wrap gap-2">
            {filterOptions.map(option => (
              <button
                key={option}
                onClick={() => onFilterChange(option)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-md border transition-colors ${
                  riscoFilter === option 
                    ? 'bg-rose-600/20 text-rose-400 border-rose-500/50 shadow-sm' 
                    : 'bg-slate-800/40 text-slate-400 border-slate-700/80 hover:bg-slate-700/50 hover:text-slate-200'
                }`}
              >
                {option === "Todos" ? <Filter className="inline w-3 h-3 mr-1" /> : null}
                {option}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-6 shrink-0">
        <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-700/50 shadow-sm flex flex-col justify-center">
          <h3 className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">Conflitos Monitorados</h3>
          <p className="text-3xl font-bold text-rose-400">{totalConflitos}</p>
        </div>
        
        <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-700/50 shadow-sm flex flex-col justify-center">
          <h3 className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">Fatalidades (6 meses)</h3>
          <p className="text-3xl font-bold text-rose-400">{totalMortes.toLocaleString('pt-BR')}</p>
        </div>
      </div>

      {/* Lista Interativa de Conflitos */}
      <div className="flex-1 overflow-y-auto pr-2 -mr-2 space-y-3 pb-8 custom-scrollbar">
        {conflitos.length === 0 ? (
          <div className="text-center py-10 opacity-70">
            <ShieldAlert className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-sm text-slate-400">Nenhum conflito encontrado com os filtros atuais.</p>
          </div>
        ) : (
          conflitos.map((c) => (
            <div 
              key={c.id_conflito}
              onClick={() => onSelect(c)}
              onMouseEnter={() => onHover(c)}
              onMouseLeave={() => onHover(null)}
              className="group cursor-pointer bg-slate-950/40 hover:bg-slate-800/60 transition-all duration-200 border border-slate-800/80 hover:border-slate-600 rounded-lg p-4 flex flex-col"
            >
              <div className="flex justify-between items-start mb-2">
                <h4 className="text-base font-bold text-slate-200 group-hover:text-white transition-colors">{c.pais}</h4>
                <div className="flex items-center gap-2">
                  {c.tendencia_previsao && (
                    <span className={`px-2 py-0.5 text-[9px] font-bold rounded uppercase tracking-wider border ${
                      c.tendencia_previsao === "Crescente"
                        ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
                        : c.tendencia_previsao === "Decrescente"
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                          : "bg-slate-500/10 text-slate-400 border-slate-500/20"
                    }`}>
                      {c.tendencia_previsao}
                    </span>
                  )}
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded uppercase tracking-wider border ${getRiskColor(c.nivel_risco)}`}>
                    {c.nivel_risco}
                  </span>
                  <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-rose-400 transition-colors" />
                </div>
              </div>
              <p className="text-xs text-slate-400 line-clamp-2 mt-1 leading-relaxed">
                {c.causa_principal}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function DetailDashboard({ conflito, onBack, onRoutesLoaded }: { conflito: ConflitoEducativo, onBack: () => void, onRoutesLoaded: (r: any[]) => void }) {
  const chartData = conflito.dados_grafico.meses.map((mes, idx) => ({
    name: mes,
    fatalidades: conflito.dados_grafico.fatalidades[idx]
  }));

  const riskColor = {
    "Crítico": "bg-rose-600 border-rose-400 text-white",
    "Alto": "bg-orange-600 border-orange-400 text-white",
    "Médio": "bg-amber-600 border-amber-400 text-white",
    "Baixo": "bg-slate-600 border-slate-400 text-white"
  }[conflito.nivel_risco] || "bg-slate-600";

  return (
    <div className="min-h-full flex flex-col p-6 pb-12">
      <button 
        onClick={onBack}
        className="flex items-center gap-2 text-sm font-medium text-slate-400 hover:text-white transition-colors mb-6 pb-4 border-b border-slate-800 w-full text-left"
      >
        <ArrowLeft className="w-4 h-4" />
        Retornar à Visão Global
      </button>

      <div className="flex items-start justify-between mb-2">
        <h2 className="text-3xl font-bold text-white tracking-tight">{conflito.pais}</h2>
        <span className={`px-3 py-1 text-xs font-bold rounded-md border shadow-sm uppercase tracking-widest ${riskColor}`}>
          Risco {conflito.nivel_risco}
        </span>
      </div>
      
      <div className="space-y-6 mt-6">
        <section>
          <h3 className="text-xs text-rose-500 font-bold uppercase tracking-widest mb-2 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4" /> Causa Principal
          </h3>
          <p className="text-sm text-slate-300 leading-relaxed bg-slate-950/40 p-4 rounded-lg border border-slate-800">
            {conflito.causa_principal}
          </p>
        </section>

        <section>
          <h3 className="text-xs text-rose-500 font-bold uppercase tracking-widest mb-3 flex items-center gap-2">
            <Users className="w-4 h-4" /> Atores Envolvidos
          </h3>
          <div className="grid grid-cols-1 gap-2">
            {conflito.atores.map((ator, idx) => (
              <div key={idx} className="flex flex-col p-3 bg-slate-800/40 border-l-2 border-amber-500 rounded-r-md">
                <span className="font-medium text-slate-200">{ator.nome}</span>
                <span className="text-xs text-slate-500">{ator.tipo}</span>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h3 className="text-xs text-rose-500 font-bold uppercase tracking-widest mb-2 flex items-center gap-2">
            <FileText className="w-4 h-4" /> Contexto Histórico
          </h3>
          <p className="text-sm text-slate-400 leading-relaxed text-justify">
            {conflito.contexto_historico}
          </p>
        </section>

        <section className="bg-slate-950/60 p-4 rounded-lg border border-slate-800">
          <h3 className="text-xs text-slate-400 font-medium uppercase tracking-widest mb-4">
            Escalada de Fatalidades (Últimos 6 meses)
          </h3>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 5, right: 0, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorFatalities" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" stroke="#475569" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '12px' }}
                  itemStyle={{ color: '#f43f5e' }}
                />
                <Area type="monotone" dataKey="fatalidades" stroke="#f43f5e" strokeWidth={2} fillOpacity={1} fill="url(#colorFatalities)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {conflito.tendencia_previsao && (
            <div className="mt-4 pt-4 border-t border-slate-800/80 flex flex-col gap-2.5 text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Tendência por Regressão Linear:</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${
                  conflito.tendencia_previsao === "Crescente"
                    ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
                    : conflito.tendencia_previsao === "Decrescente"
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                      : "bg-slate-500/10 text-slate-400 border-slate-500/20"
                }`}>
                  {conflito.tendencia_previsao}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Previsão Próximo Mês (ML):</span>
                <span className="font-bold text-rose-400 text-xs">
                  ~{conflito.previsao_fatalidades || 0} fatalidades
                </span>
              </div>
            </div>
          )}
        </section>

        {conflito.eventos_recentes && conflito.eventos_recentes.length > 0 && (
          <section className="bg-slate-950/40 p-5 rounded-lg border border-slate-800">
            <h3 className="text-xs text-rose-500 font-bold uppercase tracking-widest mb-5 flex items-center gap-2">
              <Clock className="w-4 h-4" /> Últimos Acontecimentos (ACLED)
            </h3>
            <div className="relative border-l border-slate-800 ml-2.5 pl-6 space-y-6">
              {conflito.eventos_recentes.map((evento, idx) => {
                const formatarData = (dataStr: string) => {
                  try {
                    const [ano, mes, dia] = dataStr.split('-');
                    if (!ano || !mes || !dia) return dataStr;
                    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
                    return `${dia} de ${meses[parseInt(mes, 10) - 1]}, ${ano}`;
                  } catch (e) {
                    return dataStr;
                  }
                };

                return (
                  <div key={idx} className="relative group">
                    {/* Marker Dot */}
                    <div className="absolute -left-[31px] top-1.5 w-3 h-3 rounded-full border-2 border-rose-500/80 bg-slate-900 group-hover:bg-rose-500 transition-all duration-200" />
                    
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-bold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded border border-rose-500/20 uppercase tracking-wider">
                          {evento.tipo}
                        </span>
                        <span className="text-xs font-semibold text-slate-300">
                          {evento.localizacao}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 text-[11px] text-slate-500">
                        <Calendar className="w-3 h-3" />
                        <span>{formatarData(evento.data)}</span>
                      </div>
                    </div>
                    
                    <p className="text-xs text-slate-400 leading-relaxed text-justify bg-slate-900/30 p-3 rounded border border-slate-800/50 hover:bg-slate-900/50 hover:border-slate-700/50 transition-all duration-200">
                      {evento.detalhes}
                    </p>
                    
                    {evento.fatalidades > 0 && (
                      <div className="mt-1 flex justify-end">
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          {evento.fatalidades} {evento.fatalidades === 1 ? 'morte confirmada' : 'mortes confirmadas'}
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>
        )}

        <RotasDeAcolhimento id_conflito={conflito.id_conflito} iso3={conflito.iso3} onRoutesLoaded={onRoutesLoaded} />
        
        <div className="pt-4 border-t border-slate-800 flex justify-between items-center text-xs text-slate-500">
          <span><strong>Fontes:</strong> {conflito.fonte_dados}</span>
          <span>Atualizado em {conflito.data_atualizacao}</span>
        </div>
      </div>
    </div>
  );
}
