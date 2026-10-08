import { create } from 'zustand';
import type {
  ClimateRiskDetail,
  Incident,
  IncidentSummaryResponse,
  Location,
  RiskType,
  SearchResult,
  SimulationAIExplanation,
  SimulationComparison,
} from '@/types';

interface ThemeState {
  dominantRisk: RiskType | null;
  isCritical: boolean;
  isDark: boolean;
  setDominantRisk: (risk: RiskType | null, isCritical?: boolean) => void;
  toggleDark: () => void;
}

export const useThemeStore = create<ThemeState>((set) => ({
  dominantRisk: null,
  isCritical: false,
  isDark: false,
  setDominantRisk: (dominantRisk, isCritical = false) =>
    set({ dominantRisk, isCritical }),
  toggleDark: () => set((state) => ({ isDark: !state.isDark })),
}));

interface IncidentState {
  activeIncidents: Incident[];
  selectedIncident: Incident | null;
  summary: IncidentSummaryResponse | null;
  isConnected: boolean;
  setIncidents: (incidents: Incident[]) => void;
  addIncident: (incident: Incident) => void;
  updateIncident: (incidentId: string, updates: Partial<Incident>) => void;
  removeIncident: (incidentId: string) => void;
  setSelectedIncident: (incident: Incident | null) => void;
  setSummary: (summary: IncidentSummaryResponse) => void;
  setConnected: (isConnected: boolean) => void;
}

export const useIncidentStore = create<IncidentState>((set) => ({
  activeIncidents: [],
  selectedIncident: null,
  summary: null,
  isConnected: false,
  setIncidents: (activeIncidents) => set({ activeIncidents }),
  addIncident: (incident) =>
    set((state) => ({
      activeIncidents: [
        incident,
        ...state.activeIncidents.filter((item) => item.incidentId !== incident.incidentId),
      ],
    })),
  updateIncident: (incidentId, updates) =>
    set((state) => ({
      activeIncidents: state.activeIncidents.map((incident) =>
        incident.incidentId === incidentId ? { ...incident, ...updates } : incident
      ),
      selectedIncident:
        state.selectedIncident?.incidentId === incidentId
          ? { ...state.selectedIncident, ...updates }
          : state.selectedIncident,
    })),
  removeIncident: (incidentId) =>
    set((state) => ({
      activeIncidents: state.activeIncidents.filter((incident) => incident.incidentId !== incidentId),
      selectedIncident:
        state.selectedIncident?.incidentId === incidentId ? null : state.selectedIncident,
    })),
  setSelectedIncident: (selectedIncident) => set({ selectedIncident }),
  setSummary: (summary) => set({ summary }),
  setConnected: (isConnected) => set({ isConnected }),
}));

interface LocationState {
  selectedLocation: SearchResult | null;
  searchResults: SearchResult[];
  monitoredLocations: Location[];
  setSelectedLocation: (location: SearchResult | null) => void;
  setSearchResults: (locations: SearchResult[]) => void;
  setMonitoredLocations: (locations: Location[]) => void;
}

export const useLocationStore = create<LocationState>((set) => ({
  selectedLocation: null,
  searchResults: [],
  monitoredLocations: [],
  setSelectedLocation: (selectedLocation) => set({ selectedLocation }),
  setSearchResults: (searchResults) => set({ searchResults }),
  setMonitoredLocations: (monitoredLocations) => set({ monitoredLocations }),
}));

interface SimulationState {
  isActive: boolean;
  simulatedRisks: ClimateRiskDetail | null;
  comparison: Record<RiskType, SimulationComparison> | null;
  summary: string | null;
  aiExplanation: SimulationAIExplanation | null;
  setActive: (isActive: boolean) => void;
  clearResults: () => void;
}

export const useSimulationStore = create<SimulationState>((set) => ({
  isActive: false,
  simulatedRisks: null,
  comparison: null,
  summary: null,
  aiExplanation: null,
  setActive: (isActive) => set({ isActive }),
  clearResults: () =>
    set({
      isActive: false,
      simulatedRisks: null,
      comparison: null,
      summary: null,
      aiExplanation: null,
    }),
}));

interface UIState {
  isIncidentDetailOpen: boolean;
  setIncidentDetailOpen: (isOpen: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  isIncidentDetailOpen: false,
  setIncidentDetailOpen: (isIncidentDetailOpen) => set({ isIncidentDetailOpen }),
}));
