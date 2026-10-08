'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { cn } from '@/lib/utils';
import type { Incident, Location } from '@/types';

interface EmergencyMapProps {
  incidents: Incident[];
  monitoredLocations: Location[];
  selectedIncidentId?: string;
  onIncidentSelect: (incidentId: string) => void;
  className?: string;
  height?: number;
}

const INCIDENT_COLORS: Record<string, string> = {
  HEAT: '#e0740a',
  FLOOD: '#1e6f9e',
  HEAVY_RAIN: '#3d8fc0',
  WATER_STRESS: '#8b6544',
  DROUGHT: '#b8580c',
};

const SEVERITY_SIZES = {
  WARNING: 20,
  CRITICAL: 32,
  EXTREME: 44,
};

export function EmergencyMap({
  incidents,
  monitoredLocations,
  selectedIncidentId,
  onIncidentSelect,
  className,
  height = 500,
}: EmergencyMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const markersRef = useRef<Map<string, maplibregl.Marker>>(new Map());
  const layersAdded = useRef(false);

  // Initialize map
  useEffect(() => {
    if (map.current || !mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        glyphs: 'https://demotiles.maplibre.org/font/{fontstack}/{range}.pbf',
        sources: {
          'osm-tiles': {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors',
          },
          'terrain-tiles': {
            type: 'raster',
            tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}'],
            tileSize: 256,
            attribution: '© Esri',
          },
        },
        layers: [
          {
            id: 'terrain',
            type: 'raster',
            source: 'terrain-tiles',
            paint: { 'raster-opacity': 0.6 },
          },
          {
            id: 'osm',
            type: 'raster',
            source: 'osm-tiles',
          },
        ],
      },
      center: [77.2, 22.5], // Center of India
      zoom: 4,
      minZoom: 3,
      maxZoom: 12,
    });

    map.current.on('load', () => {
      setMapLoaded(true);
      addLayers();
      updateIncidents();
      updateMonitoredLocations();
    });

    return () => {
      map.current?.remove();
      map.current = null;
      markersRef.current.forEach((marker) => marker.remove());
      markersRef.current.clear();
      layersAdded.current = false;
    };
  }, []);

  const addLayers = () => {
    if (!map.current || layersAdded.current) return;

    // Add monitored locations layer
    map.current.addSource('monitored-locations', {
      type: 'geojson',
      data: { type: 'FeatureCollection', features: [] },
    });

    map.current.addLayer({
      id: 'monitored-locations-layer',
      type: 'circle',
      source: 'monitored-locations',
      paint: {
        'circle-radius': 8,
        'circle-color': '#447a45',
        'circle-stroke-width': 2,
        'circle-stroke-color': '#fff',
        'circle-opacity': 0.7,
      },
    });

    map.current.addLayer({
      id: 'monitored-locations-label',
      type: 'symbol',
      source: 'monitored-locations',
      layout: {
        'text-field': ['get', 'name'],
        'text-font': ['Open Sans Regular'],
        'text-size': 10,
        'text-offset': [0, 1.5],
        'text-anchor': 'top',
      },
      paint: {
        'text-color': '#1a1a1a',
        'text-halo-color': '#fff',
        'text-halo-width': 1,
      },
    });

    layersAdded.current = true;
  };

  const updateMonitoredLocations = () => {
    if (!map.current || !mapLoaded) return;

    const features = monitoredLocations
      .filter((location) => Number.isFinite(location.latitude) && Number.isFinite(location.longitude))
      .map((loc) => ({
        type: 'Feature' as const,
        geometry: {
          type: 'Point' as const,
          coordinates: [loc.longitude, loc.latitude],
        },
        properties: {
          name: loc.city || loc.district || loc.state,
          locationId: loc.locationId,
        },
      }));

    const source = map.current.getSource('monitored-locations') as maplibregl.GeoJSONSource | undefined;
    source?.setData({
      type: 'FeatureCollection',
      features,
    });
  };

  const updateIncidents = () => {
    if (!map.current || !mapLoaded) return;

    // Remove old markers
    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current.clear();

    // Add new markers
    incidents.forEach((incident) => {
      const location = monitoredLocations.find((item) => item.locationId === incident.locationId);
      if (
        !location ||
        !Number.isFinite(location.latitude) ||
        !Number.isFinite(location.longitude)
      ) return;

      const color = INCIDENT_COLORS[incident.type] || '#888';
      const size = SEVERITY_SIZES[incident.severity as keyof typeof SEVERITY_SIZES] || 24;

      const el = document.createElement('div');
      el.className = 'incident-marker';
      el.style.cssText = `
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        background: ${color};
        border: 3px solid white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: ${size * 0.5}px;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        animation: pulse 2s ease-in-out infinite;
      `;
      el.innerHTML = getIncidentIcon(incident.type);
      el.title = `${incident.type} - ${incident.severity} - ${incident.riskScore}%`;

      el.addEventListener('mouseenter', () => {
        el.style.transform = 'scale(1.3)';
        el.style.boxShadow = `0 8px 24px ${color}80`;
      });
      el.addEventListener('mouseleave', () => {
        el.style.transform = 'scale(1)';
        el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
      });
      el.addEventListener('click', () => onIncidentSelect(incident.incidentId));

      const marker = new maplibregl.Marker({ element: el, anchor: 'center' })
        .setLngLat([location.longitude, location.latitude])
        .addTo(map.current!);

      markersRef.current.set(incident.incidentId, marker);
    });

    // Add pulse animation styles
    if (!document.getElementById('map-pulse-styles')) {
      const style = document.createElement('style');
      style.id = 'map-pulse-styles';
      style.textContent = `
        @keyframes pulse {
          0%, 100% { box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
          50% { box-shadow: 0 4px 12px rgba(0,0,0,0.3), 0 0 0 8px currentColor; }
        }
        .incident-marker.selected {
          box-shadow: 0 0 0 4px var(--theme-accent), 0 4px 12px rgba(0,0,0,0.3) !important;
        }
      `;
      document.head.appendChild(style);
    }

    // Update selected marker
    markersRef.current.forEach((marker, id) => {
      const el = marker.getElement();
      if (id === selectedIncidentId) {
        el.classList.add('selected');
        marker.getElement().scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
      } else {
        el.classList.remove('selected');
      }
    });
  };

  // Update when incidents or selection changes
  useEffect(() => {
    if (mapLoaded) {
      updateIncidents();
    }
  }, [incidents, selectedIncidentId, mapLoaded]);

  useEffect(() => {
    if (mapLoaded) {
      updateMonitoredLocations();
    }
  }, [monitoredLocations, mapLoaded]);

  return (
    <div
      ref={mapContainer}
      className={cn('rounded-organic overflow-hidden', className)}
      style={{ width: '100%', height }}
      role="application"
      aria-label="India emergency monitoring map"
    />
  );
}

function getIncidentIcon(type: string): string {
  const icons: Record<string, string> = {
    HEAT: '☀️',
    FLOOD: '🌊',
    HEAVY_RAIN: '🌧️',
    WATER_STRESS: '💧',
    DROUGHT: '🏜️',
  };
  return icons[type] || '⚠️';
}