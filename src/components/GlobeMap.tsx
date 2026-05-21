import React, { useRef, useEffect, useState, useMemo } from 'react';
import Map, { MapRef, Marker, Source, Layer } from 'react-map-gl/mapbox';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { ConflitoEducativo, RotaAcolhimento } from '../types';

interface GlobeMapProps {
  conflitos: ConflitoEducativo[];
  selectedConflito: ConflitoEducativo | null;
  activeConflito: ConflitoEducativo | null;
  searchQuery: string;
  flightRoutes?: RotaAcolhimento[];
  onSelect: (c: ConflitoEducativo | null) => void;
}

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN;

export default function GlobeMap({ conflitos, selectedConflito, activeConflito, searchQuery, flightRoutes, onSelect }: GlobeMapProps) {
  const mapRef = useRef<MapRef>(null);
  const [worldData, setWorldData] = useState<any>(null);
  const [mapHoveredIso, setMapHoveredIso] = useState<string | null>(null);

  // Fetch GeoJSON borders for countries
  useEffect(() => {
    fetch('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson')
      .then(res => res.json())
      .then(data => setWorldData(data))
      .catch(err => console.error("Erro ao carregar fronteiras de países", err));
  }, []);

  const styledWorldData = useMemo(() => {
    if (!worldData) return null;
    const conflictIsos = conflitos.map(c => c.iso3);
    const hostIsos = ['CAN', 'DEU', 'UGA', 'AUS']; // Colômbia (COL) já é conflito, deixamos o conflito prevalecer (vermelho)

    const newFeatures = worldData.features.map((f: any) => {
      const iso = f.properties['ISO3166-1-Alpha-3'];
      let colorType = 'normal';
      if (conflictIsos.includes(iso)) colorType = 'conflict';
      else if (hostIsos.includes(iso)) colorType = 'host';

      return {
        ...f,
        properties: {
          ...f.properties,
          colorType
        }
      };
    });

    return {
      ...worldData,
      features: newFeatures
    };
  }, [worldData, conflitos]);

  useEffect(() => {
    if (selectedConflito && mapRef.current) {
      mapRef.current.flyTo({
        center: [selectedConflito.longitude, selectedConflito.latitude],
        zoom: 4.5,
        pitch: 50,
        duration: 2500,
      });
    }
  }, [selectedConflito]);

  const [pinnedIso, setPinnedIso] = useState<string | null>(null);

  useEffect(() => {
    // If selectedConflito changes (e.g. from dashboard click), unpin local selection
    if (selectedConflito) {
      setPinnedIso(null);
    }
  }, [selectedConflito]);

  const searchedIso = useMemo(() => {
    if (!worldData || !searchQuery || searchQuery.length < 3) return null;
    const q = searchQuery.toLowerCase();
    
    // Very basic Portuguese to English fallback for common non-conflict countries
    const PT_EN_MAP: Record<string, string> = {
      'brasil': 'brazil',
      'eua': 'united states',
      'estados unidos': 'united states',
      'inglaterra': 'united kingdom',
      'reino unido': 'united kingdom',
      'frança': 'france',
      'espanha': 'spain',
      'alemanha': 'germany',
      'itália': 'italy',
      'china': 'china',
      'japão': 'japan',
      'índia': 'india',
      'méxico': 'mexico',
      'argentina': 'argentina'
    };

    const target = PT_EN_MAP[q] || q;

    const feat = worldData.features.find((f: any) => 
      f.properties.name?.toLowerCase().includes(target) ||
      f.properties['ISO3166-1-Alpha-3']?.toLowerCase() === q ||
      f.properties.ADMIN?.toLowerCase().includes(target)
    );
    return feat ? feat.properties['ISO3166-1-Alpha-3'] : null;
  }, [searchQuery, worldData]);

  const activeIso = activeConflito?.iso3 || pinnedIso || searchedIso;

  const activeFeature = useMemo(() => {
    if (!worldData || !activeIso) return null;
    const feature = worldData.features.find((f: any) => f.properties['ISO3166-1-Alpha-3'] === activeIso);
    if (!feature) return null;
    return {
      type: 'FeatureCollection',
      features: [feature]
    };
  }, [worldData, activeIso]);

  const mapHoveredFeature = useMemo(() => {
    // Only show map hover if it's different from the already active feature to prevent overlap
    if (!worldData || !mapHoveredIso || mapHoveredIso === activeIso) return null;
    const feature = worldData.features.find((f: any) => f.properties['ISO3166-1-Alpha-3'] === mapHoveredIso);
    if (!feature) return null;
    return {
      type: 'FeatureCollection',
      features: [feature]
    };
  }, [worldData, mapHoveredIso, activeIso]);

  const flightRoutesGeoJSON = useMemo(() => {
    if (!flightRoutes || flightRoutes.length === 0 || !selectedConflito) return null;
    
    const lines = flightRoutes
      .filter(rota => rota.destino_lat !== undefined && rota.destino_lon !== undefined && rota.disponivel)
      .map(rota => ({
        type: 'Feature',
        geometry: {
          type: 'LineString',
          coordinates: [
            [selectedConflito.longitude, selectedConflito.latitude],
            [rota.destino_lon, rota.destino_lat]
          ]
        },
        properties: {
          pais: rota.pais
        }
      }));

    if (lines.length === 0) return null;

    return {
      type: 'FeatureCollection',
      features: lines
    };
  }, [flightRoutes, selectedConflito]);

  if (!MAPBOX_TOKEN) {
    return (
      <div className="h-full w-full flex items-center justify-center p-8 bg-slate-900 border border-red-500/30">
        <div className="max-w-lg text-center space-y-4">
          <div className="w-16 h-16 mx-auto rounded-full bg-red-500/10 flex items-center justify-center mb-6">
            <svg className="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-red-400">Mapbox Token Ausente</h2>
          <p className="text-slate-400">
            A visualização do globo geolocalizado requer uma chave de API válida do Mapbox.
          </p>
          <div className="bg-slate-950 p-4 rounded-md text-left font-mono text-sm border border-slate-800">
            <p className="text-emerald-400 mb-2"># Adicione ao seu arquivo .env.example</p>
            <p className="text-slate-200">VITE_MAPBOX_TOKEN="sua_chave_aqui"</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Map
      ref={mapRef}
      mapboxAccessToken={MAPBOX_TOKEN}
      initialViewState={{
        longitude: 0,
        latitude: 20,
        zoom: 1.8,
        pitch: 0,
      }}
      mapStyle="mapbox://styles/mapbox/dark-v11"
      projection={{ name: 'globe' }}
      fog={{
        range: [0.5, 10],
        color: 'rgb(20, 24, 36)',
        'high-color': 'rgb(36, 92, 223)',
        'space-color': 'rgb(11, 11, 25)',
        'star-intensity': 0.8
      }}
      interactiveLayerIds={['countries-interactive']}
      onMouseMove={(e) => {
        if (e.features && e.features.length > 0) {
          const iso = e.features[0].properties?.['ISO3166-1-Alpha-3'];
          if (iso && iso !== mapHoveredIso) {
            setMapHoveredIso(iso);
          }
        } else if (mapHoveredIso) {
          setMapHoveredIso(null);
        }
      }}
      onMouseLeave={() => setMapHoveredIso(null)}
      onClick={(e) => {
        if (e.features && e.features.length > 0) {
          const iso = e.features[0].properties?.['ISO3166-1-Alpha-3'];
          if (iso) {
            setPinnedIso(iso);
            const conflict = conflitos.find(c => c.iso3 === iso);
            if (conflict) {
              onSelect(conflict);
            } else {
              onSelect(null);
            }
          } else {
            setPinnedIso(null);
            onSelect(null);
          }
        } else {
          setPinnedIso(null);
          onSelect(null);
        }
      }}
      cursor="grab"
    >
      {styledWorldData && (
        <Source id="all-countries" type="geojson" data={styledWorldData}>
          <Layer
            id="countries-interactive"
            type="fill"
            paint={{
              'fill-color': [
                'match',
                ['get', 'colorType'],
                'conflict', '#ef4444', // Vermelho para conflito
                'host', '#4ade80',     // Verde suave para acolhimento
                '#8b5cf6'              // Roxo para os demais
              ],
              'fill-opacity': [
                'match',
                ['get', 'colorType'],
                'conflict', 0.2,
                'host', 0.2,
                0.05
              ]
            }}
          />
        </Source>
      )}

      {mapHoveredFeature && (
        <Source id="map-hovered-country" type="geojson" data={mapHoveredFeature as any}>
          {/* Subtle gradient effect related to map style (slate/indigo vibes) */}
          <Layer 
            id="map-hover-glow"
            type="line"
            paint={{
              'line-color': '#4f46e5', // indigo-600
              'line-width': 12,
              'line-blur': 15,
              'line-opacity': 0.3
            }}
          />
          <Layer 
            id="map-hover-border"
            type="line"
            paint={{
              'line-color': '#6366f1', // indigo-500
              'line-width': 1.5,
              'line-opacity': 0.6
            }}
          />
          <Layer 
            id="map-hover-fill"
            type="fill"
            paint={{
              'fill-color': '#4f46e5',
              'fill-opacity': 0.1
            }}
          />
        </Source>
      )}
      {activeFeature && (
        <Source id="highlighted-country" type="geojson" data={activeFeature as any}>
          {/* Subtle gradient effect related to map style (slate/indigo vibes) */}
          <Layer 
            id="active-glow"
            type="line"
            paint={{
              'line-color': '#4f46e5', // indigo-600
              'line-width': 14,
              'line-blur': 15,
              'line-opacity': 0.5
            }}
          />
          <Layer 
            id="active-border"
            type="line"
            paint={{
              'line-color': '#818cf8', // indigo-400
              'line-width': 2,
              'line-opacity': 0.9
            }}
          />
          <Layer 
            id="active-fill"
            type="fill"
            paint={{
              'fill-color': '#4f46e5',
              'fill-opacity': 0.2
            }}
          />
        </Source>
      )}

      {flightRoutesGeoJSON && (
        <Source id="flight-routes" type="geojson" data={flightRoutesGeoJSON as any}>
          {/* Fundo da linha para dar contraste */}
          <Layer 
            id="flight-route-bg"
            type="line"
            paint={{
              'line-color': '#000000',
              'line-width': 4,
              'line-opacity': 0.3
            }}
          />
          {/* Linha tracejada verde humanitária */}
          <Layer 
            id="flight-route-dashed"
            type="line"
            paint={{
              'line-color': '#4ade80', // Verde de acolhimento
              'line-width': 2,
              'line-dasharray': [3, 3],
              'line-opacity': 0.9
            }}
          />
        </Source>
      )}

      {conflitos.map(c => {
        // Mapeando do raio em km para um tamanho visual (em pixels) para o pulso CSS 
        // Isso garante que o pulso fique relativo à área de afecção global
        const scaleBase = c.raio_km / 10;
        const pulseSize = Math.max(scaleBase, 30); // Define um mínimo para que sempre fique visível
        const isSelected = selectedConflito?.id_conflito === c.id_conflito;

        return (
          <Marker
            key={c.id_conflito}
            longitude={c.longitude}
            latitude={c.latitude}
            anchor="center"
            onClick={(e) => {
              e.originalEvent.stopPropagation();
              onSelect(c);
            }}
          >
            <div 
              className={`marker-container ${isSelected ? 'marker-selected' : ''}`} 
              style={{ '--pulse-size': `${isSelected ? pulseSize * 1.2 : pulseSize}px` } as React.CSSProperties}
            >
              <div className="marker-pulse"></div>
              <div className="marker-pulse-delay"></div>
              <div className="marker-central"></div>
            </div>
          </Marker>
        );
      })}
    </Map>
  );
}
