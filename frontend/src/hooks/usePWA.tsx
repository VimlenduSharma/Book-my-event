import { useState, useEffect } from 'react';
import { Event } from '@/types/Event';

export const usePWA = () => {
  const [isOffline, setIsOffline] = useState(false);
  const [cachedEvents, setCachedEvents] = useState<Event[]>([]);

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Load cached events
    const cached = localStorage.getItem('cached-events');
    if (cached) {
      setCachedEvents(JSON.parse(cached));
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const cacheEvents = (events: Event[]) => {
    localStorage.setItem('cached-events', JSON.stringify(events));
    setCachedEvents(events);
  };

  return {
    isOffline,
    cachedEvents,
    cacheEvents
  };
};
