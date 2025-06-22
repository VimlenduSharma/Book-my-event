import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { format } from "date-fns";
import { ArrowLeft, Calendar, Download, ExternalLink, AlertCircle } from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface Booking {
  id: string;
  eventTitle: string;
  eventId: string;
  host: string;
  datetime: Date;
  duration: number;
  status: 'confirmed' | 'cancelled' | 'pending';
  attendeeName: string;
  attendeeEmail: string;
  price: number;
}

const mockBookings: Booking[] = [
  {
    id: "b1",
    eventTitle: "Product Strategy Session",
    eventId: "1",
    host: "Sarah Johnson",
    datetime: new Date(2024, 6, 25, 14, 0),
    duration: 60,
    status: 'confirmed',
    attendeeName: "John Doe",
    attendeeEmail: "john@example.com",
    price: 0
  },
  {
    id: "b2",
    eventTitle: "Technical Architecture Review",
    eventId: "2",
    host: "Mike Chen",
    datetime: new Date(2024, 6, 28, 10, 30),
    duration: 90,
    status: 'confirmed',
    attendeeName: "John Doe",
    attendeeEmail: "john@example.com",
    price: 150
  },
  {
    id: "b3",
    eventTitle: "Design Workshop",
    eventId: "3",
    host: "Emma Davis",
    datetime: new Date(2024, 6, 15, 16, 0),
    duration: 120,
    status: 'cancelled',
    attendeeName: "John Doe",
    attendeeEmail: "john@example.com",
    price: 75
  },
  {
    id: "b4",
    eventTitle: "Investment Pitch Session",
    eventId: "4",
    host: "Robert Smith",
    datetime: new Date(2024, 7, 2, 11, 0),
    duration: 45,
    status: 'pending',
    attendeeName: "John Doe",
    attendeeEmail: "john@example.com",
    price: 200
  }
];

const MyBookings = () => {
  const navigate = useNavigate();
  const [bookings] = useState<Booking[]>(mockBookings);
  const [filter, setFilter] = useState<'all' | 'upcoming' | 'past'>('all');

  const now = new Date();
  const filteredBookings = bookings.filter(booking => {
    if (filter === 'upcoming') return booking.datetime > now;
    if (filter === 'past') return booking.datetime < now;
    return true;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const addToGoogleCalendar = (booking: Booking) => {
    const startTime = booking.datetime.toISOString().replace(/[-:]/g, '').split('.')[0];
    const endTime = new Date(booking.datetime.getTime() + booking.duration * 60000)
      .toISOString().replace(/[-:]/g, '').split('.')[0];
    
    const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(booking.eventTitle)}&dates=${startTime}Z/${endTime}Z&details=${encodeURIComponent(`Session with ${booking.host}`)}&location=Online`;
    
    window.open(url, '_blank');
  };

  const downloadICS = (booking: Booking) => {
    const startTime = booking.datetime.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    const endTime = new Date(booking.datetime.getTime() + booking.duration * 60000)
      .toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    
    const icsContent = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//ScheduleHub//EN',
      'BEGIN:VEVENT',
      `DTSTART:${startTime}`,
      `DTEND:${endTime}`,
      `SUMMARY:${booking.eventTitle}`,
      `DESCRIPTION:Session with ${booking.host}`,
      'LOCATION:Online',
      `UID:${booking.id}@schedulehub.com`,
      'END:VEVENT',
      'END:VCALENDAR'
    ].join('\r\n');

    const blob = new Blob([icsContent], { type: 'text/calendar' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${booking.eventTitle.replace(/\s+/g, '_')}.ics`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const cancelBooking = (bookingId: string) => {
    toast({
      title: "Booking cancelled",
      description: "Your booking has been cancelled successfully.",
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <Button variant="ghost" onClick={() => navigate('/')} className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Events
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Bookings</h1>
          <p className="text-gray-600">Manage your scheduled sessions and appointments</p>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-2 mb-6">
          {[
            { key: 'all', label: 'All Bookings' },
            { key: 'upcoming', label: 'Upcoming' },
            { key: 'past', label: 'Past' }
          ].map(({ key, label }) => (
            <Button
              key={key}
              variant={filter === key ? 'default' : 'outline'}
              onClick={() => setFilter(key as any)}
            >
              {label}
            </Button>
          ))}
        </div>

        {/* Bookings Table */}
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle>Your Sessions ({filteredBookings.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {filteredBookings.length === 0 ? (
              <div className="text-center py-12">
                <Calendar className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No bookings found</h3>
                <p className="text-gray-600 mb-6">You haven't booked any sessions yet.</p>
                <Button onClick={() => navigate('/')}>
                  Browse Events
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Event</TableHead>
                      <TableHead>Host</TableHead>
                      <TableHead>Date & Time</TableHead>
                      <TableHead>Duration</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Price</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredBookings.map((booking) => (
                      <TableRow key={booking.id}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{booking.eventTitle}</p>
                            <Button
                              variant="link"
                              size="sm"
                              className="p-0 h-auto text-indigo-600"
                              onClick={() => navigate(`/event/${booking.eventId}`)}
                            >
                              View Event <ExternalLink className="h-3 w-3 ml-1" />
                            </Button>
                          </div>
                        </TableCell>
                        <TableCell>{booking.host}</TableCell>
                        <TableCell>
                          <div>
                            <p className="font-medium">{format(booking.datetime, 'MMM d, yyyy')}</p>
                            <p className="text-sm text-gray-500">{format(booking.datetime, 'h:mm a')}</p>
                          </div>
                        </TableCell>
                        <TableCell>{booking.duration} min</TableCell>
                        <TableCell>
                          <Badge className={getStatusColor(booking.status)}>
                            {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {booking.price === 0 ? 'Free' : `$${booking.price}`}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            {booking.status === 'confirmed' && booking.datetime > now && (
                              <>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => addToGoogleCalendar(booking)}
                                  title="Add to Google Calendar"
                                >
                                  <Calendar className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => downloadICS(booking)}
                                  title="Download ICS"
                                >
                                  <Download className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => cancelBooking(booking.id)}
                                  className="text-red-600 hover:text-red-700"
                                  title="Cancel Booking"
                                >
                                  <AlertCircle className="h-4 w-4" />
                                </Button>
                              </>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MyBookings;
