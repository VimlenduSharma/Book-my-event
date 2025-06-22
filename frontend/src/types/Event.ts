export interface Event {
  id: string;
  title: string;
  host: string;
  description: string;
  availableSlots: number;
  totalSlots: number;
  duration: number; // in minutes
  price: number; // 0 for free events
  category: string;
  rating: number;
  image?: string;
  timezone: string;
  slots?: TimeSlot[];
}

export interface TimeSlot {
  id: string;
  datetime: Date;
  available: boolean;
  eventId: string;
}

export interface Booking {
  id: string;
  eventId: string;
  slotId: string;
  attendeeName: string;
  attendeeEmail: string;
  createdAt: Date;
  status: 'confirmed' | 'pending' | 'cancelled';
}
