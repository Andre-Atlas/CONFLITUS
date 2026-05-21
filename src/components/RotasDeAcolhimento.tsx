import React, { useState } from 'react';
import { PlaneTakeoff, Clock, Plane, AlertCircle, XCircle } from 'lucide-react';

import { RotaAcolhimento } from '../types';

interface RotasDeAcolhimentoProps {
  id_conflito: string;
  iso3: string;
  onRoutesLoaded: (rotas: RotaAcolhimento[]) => void;
}

export default function RotasDeAcolhimento({ id_conflito, iso3, onRoutesLoaded }: RotasDeAcolhimentoProps) {
  const [rotas, setRotas] = useState<RotaAcolhimento[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const buscarRotas = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/conflitos/${id_conflito}/rotas-fuga?iso3=${iso3}`);
      if (!res.ok) {
        throw new Error('Falha ao conectar com o serviço de malha aérea.');
      }
      const data = await res.json();
      if (data.erro) {
        throw new Error(data.erro);
      }
      setRotas(data.opcoes);
      onRoutesLoaded(data.opcoes);
    } catch (err: any) {
      setError(err.message);
      onRoutesLoaded([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="bg-slate-900 border-t-2 border-rose-500/30 p-4 mt-6 rounded-lg shadow-lg">
      <h3 className="text-xs text-rose-500 font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
        <PlaneTakeoff className="w-4 h-4" /> Vias de Fuga e Acolhimento
      </h3>
      
      {!rotas && !loading && !error && (
        <div className="text-center p-4 bg-slate-950/40 rounded-md border border-slate-800">
          <p className="text-xs text-slate-400 mb-3">Busque conexões aéreas humanitárias em tempo real para os 5 países parceiros de acolhimento.</p>
          <button 
            onClick={buscarRotas}
            className="w-full py-2 bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold uppercase tracking-wider rounded transition-colors"
          >
            Buscar Voos de Urgência
          </button>
        </div>
      )}

      {loading && (
        <div className="flex flex-col items-center justify-center p-6 space-y-3">
          <div className="w-6 h-6 border-2 border-rose-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs text-rose-400 animate-pulse tracking-widest uppercase">Consultando Duffel API...</p>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-950/30 border border-red-500/30 rounded flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-red-500 mt-0.5" />
          <p className="text-xs text-red-400">{error}</p>
        </div>
      )}

      {rotas && !loading && (
        <div className="space-y-2 mt-2">
          {rotas.map((rota, idx) => (
            <div key={idx} className={`p-3 rounded-md border flex flex-col gap-1 transition-all ${rota.disponivel ? 'bg-slate-800/60 border-slate-700 hover:border-slate-500' : 'bg-slate-950/50 border-red-900/30 opacity-75'}`}>
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-200 text-sm">{rota.pais}</span>
                  <span className="text-[10px] bg-slate-700 text-slate-300 px-1.5 py-0.5 rounded">{rota.destino_iata}</span>
                </div>
                {rota.disponivel ? (
                  <span className="text-sm font-black text-emerald-400">{rota.preco}</span>
                ) : (
                  <span className="text-xs font-bold text-red-500 flex items-center gap-1"><XCircle className="w-3 h-3"/> Indisponível</span>
                )}
              </div>
              
              {rota.disponivel ? (
                <div className="flex justify-between items-center text-xs text-slate-400 mt-1">
                  <span className="flex items-center gap-1"><Plane className="w-3 h-3"/> {rota.companhia_aerea}</span>
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3"/> {rota.duracao} ({rota.escalas} escala{rota.escalas !== 1 ? 's' : ''})</span>
                </div>
              ) : (
                <p className="text-[10px] text-red-400/80 italic">{rota.mensagem}</p>
              )}
            </div>
          ))}
          <button 
            onClick={() => {
              setRotas(null);
              onRoutesLoaded([]);
            }}
            className="w-full mt-3 py-1.5 text-[10px] text-slate-500 hover:text-slate-300 uppercase tracking-widest transition-colors"
          >
            Limpar Busca
          </button>
        </div>
      )}
    </section>
  );
}
