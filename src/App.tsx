import React, { useEffect, useState } from 'react';
import { ConflitoEducativo, RotaAcolhimento } from './types';
import GlobeMap from './components/GlobeMap';
import Dashboard from './components/Dashboard';

export default function App() {
  const [conflitos, setConflitos] = useState<ConflitoEducativo[]>([]);
  const [selectedConflito, setSelectedConflito] = useState<ConflitoEducativo | null>(null);
  const [hoveredConflito, setHoveredConflito] = useState<ConflitoEducativo | null>(null);
  const [riscoFilter, setRiscoFilter] = useState<string>('Todos');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [flightRoutes, setFlightRoutes] = useState<RotaAcolhimento[]>([]);

  // Limpar rotas de voo ao selecionar/deselecionar um conflito
  const handleSelectConflito = (c: ConflitoEducativo | null) => {
    setSelectedConflito(c);
    setFlightRoutes([]);
  };

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('/api/conflitos');
        if (!res.ok) throw new Error('Não foi possível carregar os dados.');
        const data = await res.json();
        setConflitos(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const filteredConflitos = conflitos.filter(c => {
    const matchRisco = riscoFilter === 'Todos' || c.nivel_risco === riscoFilter;
    const matchSearch = c.pais.toLowerCase().includes(searchQuery.toLowerCase());
    return matchRisco && matchSearch;
  });

  // Determines which country border to highlight: hovered, selected, or implicitly searched
  const activeFocus = hoveredConflito || selectedConflito || (filteredConflitos.length === 1 && searchQuery.length > 1 ? filteredConflitos[0] : null);

  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-200 overflow-hidden font-sans">
      <div className="flex-[7] relative h-full">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-950 z-10">
            <div className="text-blue-400 font-mono tracking-widest uppercase animate-pulse">Carregando Globo Sensorial...</div>
          </div>
        ) : error ? (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-950 text-red-500 z-10">
            {error}
          </div>
        ) : (
          <GlobeMap 
            conflitos={filteredConflitos} 
            selectedConflito={selectedConflito} 
            activeConflito={activeFocus}
            searchQuery={searchQuery}
            onSelect={handleSelectConflito} 
            flightRoutes={flightRoutes}
          />
        )}
      </div>

      <div className="flex-[3] h-full shadow-[-10px_0_30px_rgba(0,0,0,0.5)] z-20 bg-slate-900 border-l border-slate-800 overflow-y-auto">
        <Dashboard 
          conflitos={filteredConflitos} 
          selectedConflito={selectedConflito} 
          onBack={() => handleSelectConflito(null)} 
          riscoFilter={riscoFilter}
          onFilterChange={setRiscoFilter}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          onSelect={handleSelectConflito}
          onHover={setHoveredConflito}
          onRoutesLoaded={setFlightRoutes}
        />
      </div>
    </div>
  );
}
