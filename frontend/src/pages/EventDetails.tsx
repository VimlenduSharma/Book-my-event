import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Clock, Users, Star, MapPin, Share2, Calendar, DollarSign } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Event, TimeSlot } from "@/types/Event";
import SlotCalendar from "@/components/SlotCalendar";
import BookingForm from "@/components/BookingForm";
import TimezoneSwitch from "@/components/TimezoneSwitch";
import AdminBanner from "@/components/AdminBanner";
import { useToast } from "@/hooks/use-toast";

const mockTimeSlots: TimeSlot[] = [
  { id: "1", datetime: new Date("2024-01-15T09:00:00"), available: true, eventId: "1" },
  { id: "2", datetime: new Date("2024-01-15T10:30:00"), available: true, eventId: "1" },
  { id: "3", datetime: new Date("2024-01-15T14:00:00"), available: false, eventId: "1" },
  { id: "4", datetime: new Date("2024-01-16T09:00:00"), available: true, eventId: "1" },
  { id: "5", datetime: new Date("2024-01-16T11:00:00"), available: true, eventId: "1" },
  { id: "6", datetime: new Date("2024-01-17T13:00:00"), available: true, eventId: "1" },
];

const mockEvent: Event = {
  id: "1",
  title: "Product Strategy Session",
  host: "Sarah Johnson",
  description: "Join me for an in-depth product strategy session where we'll discuss your product roadmap, market positioning, and growth strategies. This session is perfect for startup founders, product managers, and entrepreneurs looking to refine their product vision and create actionable plans for success.\n\nWhat you'll get:\n• Comprehensive product audit\n• Strategic roadmap development\n• Market analysis and competitive insights\n• Actionable next steps\n\nI bring 10+ years of experience from leading product teams at Fortune 500 companies and successful startups.",
  availableSlots: 12,
  totalSlots: 15,
  duration: 60,
  price: 0,
  category: "Business",
  rating: 4.9,
  image: "https://images.unsplash.com/photo-1649972904349-6e44c42644a7?w=1200&h=800&fit=crop",
  timezone: "America/New_York",
  slots: mockTimeSlots
};

const EventDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [event, setEvent] = useState<Event | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);
  const [loading, setLoading] = useState(true);
  const [timezone, setTimezone] = useState(Intl.DateTimeFormat().resolvedOptions().timeZone);
  const [isCreator, setIsCreator] = useState(false);

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setEvent(mockEvent);
      setLoading(false);
      // Simulate checking if current user is the creator
      setIsCreator(Math.random() > 0.7); // 30% chance to show admin banner
    }, 1000);
  }, [id]);

  const handleCopyLink = () => {
    const link = selectedSlot 
      ? `${window.location.href}?slot=${selectedSlot.id}`
      : window.location.href;
    navigator.clipboard.writeText(link);
    toast({
      title: "Link copied!",
      description: selectedSlot 
        ? "Event link with selected slot has been copied to your clipboard."
        : "Event link has been copied to your clipboard.",
    });
  };

  const handleSlotSelect = (slot: TimeSlot) => {
    setSelectedSlot(slot);
  };

  const handleEditEvent = () => {
    navigate(`/edit-event/${id}`);
  };

  const handleDeleteEvent = () => {
    if (confirm('Are you sure you want to delete this event?')) {
      toast({
        title: "Event deleted",
        description: "Your event has been successfully deleted.",
        variant: "destructive"
      });
      navigate('/');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex flex-col items-center justify-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Event not found</h1>
        <Button onClick={() => navigate("/")} variant="outline">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Button 
              variant="ghost" 
              onClick={() => navigate("/")}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Events
            </Button>
            
            <div className="flex items-center gap-3">
              <TimezoneSwitch value={timezone} onChange={setTimezone} />
              <Button 
                variant="outline" 
                onClick={handleCopyLink}
                className="flex items-center gap-2"
              >
                <Share2 className="h-4 w-4" />
                Copy Link
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Admin Banner */}
        {isCreator && (
          <AdminBanner 
            eventId={event.id}
            onEdit={handleEditEvent}
            onDelete={handleDeleteEvent}
          />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Hero Section */}
            <Card className="overflow-hidden shadow-xl border-0">
              <div className="aspect-[16/9] relative">
                {event.image && (
                  <img
                    src={event.image}
                    alt={event.title}
                    className="w-full h-full object-cover"
                  />
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
                <div className="absolute bottom-6 left-6 right-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Badge className="bg-white/20 text-white backdrop-blur-sm">
                      {event.category}
                    </Badge>
                    {event.price > 0 && (
                      <Badge className="bg-green-600 text-white">
                        <DollarSign className="h-3 w-3 mr-1" />
                        ${event.price}
                      </Badge>
                    )}
                  </div>
                  <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
                    {event.title}
                  </h1>
                  <p className="text-white/90 text-lg">with {event.host}</p>
                </div>
              </div>
            </Card>

            {/* Event Info */}
            <Card className="shadow-lg border-0">
              <CardContent className="p-8">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                  <div className="text-center">
                    <div className="bg-indigo-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
                      <Clock className="h-8 w-8 text-indigo-600" />
                    </div>
                    <p className="font-semibold text-gray-900">{event.duration} minutes</p>
                    <p className="text-sm text-gray-600">Duration</p>
                  </div>
                  
                  <div className="text-center">
                    <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
                      <Users className="h-8 w-8 text-green-600" />
                    </div>
                    <p className="font-semibold text-gray-900">{event.availableSlots}/{event.totalSlots}</p>
                    <p className="text-sm text-gray-600">Available</p>
                  </div>
                  
                  <div className="text-center">
                    <div className="bg-yellow-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
                      <Star className="h-8 w-8 text-yellow-600 fill-current" />
                    </div>
                    <p className="font-semibold text-gray-900">{event.rating}</p>
                    <p className="text-sm text-gray-600">Rating</p>
                  </div>
                  
                  <div className="text-center">
                    <div className="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
                      <MapPin className="h-8 w-8 text-purple-600" />
                    </div>
                    <p className="font-semibold text-gray-900">Online</p>
                    <p className="text-sm text-gray-600">Location</p>
                  </div>
                </div>

                <div className="prose prose-lg max-w-none">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">About this session</h3>
                  <div className="text-gray-700 whitespace-pre-line leading-relaxed">
                    {event.description}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Slot Calendar */}
            <Card className="shadow-lg border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-2xl">
                  <Calendar className="h-6 w-6 text-indigo-600" />
                  Available Time Slots
                </CardTitle>
                <p className="text-gray-600">
                  Times shown in {timezone.replace('_', ' ')} timezone
                </p>
              </CardHeader>
              <CardContent>
                <SlotCalendar 
                  slots={event.slots || []}
                  onSlotSelect={handleSlotSelect}
                  selectedSlot={selectedSlot}
                  timezone={timezone}
                />
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <BookingForm 
              event={event}
              selectedSlot={selectedSlot}
              onSlotSelect={handleSlotSelect}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventDetails;
