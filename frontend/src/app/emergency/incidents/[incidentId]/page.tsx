'use client';

import { useEffect, useState } from 'react';
import { IncidentDetail } from '@/components/emergency/IncidentDetail';
import { useIncidentStore, useLocationStore, useUIStore } from '@/store';
import { api } from '@/lib/api';
import type { Incident, IncidentTimelineResponse } from '@/types';
import { useParams, useRouter } from 'next/navigation';

export default function IncidentDetailPage() {
  const router = useRouter();
  const params = useParams();
  const incidentId = params.incidentId as string;
  const { activeIncidents, setSelectedIncident } = useIncidentStore();
  const { monitoredLocations } = useLocationStore();
  const { setIncidentDetailOpen } = useUIStore();

  const [incident, setIncident] = useState<Incident | null>(null);
  const [timeline, setTimeline] = useState<IncidentTimelineResponse['timeline']>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (incidentId) {
      fetchIncidentData();
    }
  }, [incidentId]);

  const fetchIncidentData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [incidentRes, timelineRes] = await Promise.all([
        api.getIncident(incidentId),
        api.getIncidentTimeline(incidentId),
      ]);
      setIncident(incidentRes);
      setTimeline(timelineRes.timeline);
      setSelectedIncident(incidentRes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load incident');
    } finally {
      setIsLoading(false);
    }
  };

  const locationName = incident
    ? monitoredLocations.find(l => l.locationId === incident.locationId)?.city
    : undefined;

  const handleClose = () => {
    setSelectedIncident(null);
    setIncidentDetailOpen(false);
    router.back();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-theme-bg-primary">
        <div className="text-center">
          <div className="text-6xl mb-4 animate-pulse">📋</div>
          <p className="text-theme-text-secondary">Loading incident details...</p>
        </div>
      </div>
    );
  }

  if (error || !incident) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-theme-bg-primary">
        <div className="container max-w-md mx-auto px-6">
          <div className="card-organic p-8 text-center">
            <span className="text-6xl mb-4 block">⚠️</span>
            <h2 className="font-heading text-h2 text-theme-text-primary mb-2">Unable to Load Incident</h2>
            <p className="text-theme-text-secondary mb-6">{error || 'Incident not found'}</p>
            <button
              onClick={handleClose}
              className="btn-primary"
            >
              Back to Command Center
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <IncidentDetail
      incident={incident}
      timeline={timeline}
      locationName={locationName}
      onClose={handleClose}
    />
  );
}