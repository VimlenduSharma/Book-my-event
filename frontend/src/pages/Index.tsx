import { useState, useEffect } from "react";
import { Calendar, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import EventCard from "@/components/EventCard";
import AddEventCard from "@/components/AddEventCard";
import SkeletonLoader from "@/components/SkeletonLoader";
import ThemeToggle from "@/components/ThemeToggle";
import CurrencySelector from "@/components/CurrencySelector";
import LocaleSwitch from "@/components/LocaleSwitch";
import GlobalSearch from "@/components/GlobalSearch";
import AnalyticsOptIn from "@/components/AnalyticsOptIn";
import { Event } from "@/types/Event";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from 'react-i18next';
import { usePWA } from '@/hooks/usePWA';
import { Badge } from "@/components/ui/badge";

const mockEvents: Event[] = [
  {
    id: "1",
    title: "Product Strategy Session",
    host: "Sarah Johnson",
    description: "Discuss product roadmap and strategic initiatives for Q2",
    availableSlots: 12,
    totalSlots: 15,
    duration: 60,
    price: 0,
    category: "Business",
    rating: 4.9,
    image: "https://images.unsplash.com/photo-1649972904349-6e44c42644a7?w=800&h=600&fit=crop",
    timezone: "America/New_York"
  },
  {
    id: "2", 
    title: "Technical Architecture Review",
    host: "Mike Chen",
    description: "Deep dive into system architecture and technical decisions",
    availableSlots: 3,
    totalSlots: 8,
    duration: 90,
    price: 150,
    category: "Technology",
    rating: 4.8,
    image: "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=800&h=600&fit=crop",
    timezone: "America/Los_Angeles"
  },
  {
    id: "3",
    title: "Design Workshop",
    host: "Emma Davis",
    description: "Collaborative design thinking session for new features",
    availableSlots: 8,
    totalSlots: 10,
    duration: 120,
    price: 75,
    category: "Design",
    rating: 5.0,
    image: "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&h=600&fit=crop",
    timezone: "Europe/London"
  },
  {
    id: "4",
    title: "Investment Pitch Session",
    host: "Robert Smith",
    description: "Present your startup idea to experienced investors",
    availableSlots: 5,
    totalSlots: 6,
    duration: 45,
    price: 200,
    category: "Business",
    rating: 4.7,
    image: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=800&h=600&fit=crop",
    timezone: "America/New_York"
  },
  {
    id: "5",
    title: "Marketing Strategy Consultation",
    host: "Lisa Wang",
    description: "Get expert advice on your marketing campaigns and brand positioning",
    availableSlots: 7,
    totalSlots: 10,
    duration: 60,
    price: 120,
    category: "Marketing",
    rating: 4.6,
    image: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&h=600&fit=crop",
    timezone: "America/Chicago"
  },
  {
    id: "6",
    title: "Data Science Workshop",
    host: "Dr. Alex Kumar",
    description: "Learn advanced data analysis techniques and machine learning basics",
    availableSlots: 15,
    totalSlots: 20,
    duration: 180,
    price: 0,
    category: "Technology",
    rating: 4.9,
    image: "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&h=600&fit=crop",
    timezone: "Asia/Tokyo"
  },
  {
    id: "7",
    title: "Career Mentorship Session",
    host: "Jennifer Brown",
    description: "One-on-one career guidance and professional development advice",
    availableSlots: 4,
    totalSlots: 6,
    duration: 45,
    price: 80,
    category: "Career",
    rating: 4.8,
    image: "https://images.unsplash.com/photo-1487058792275-0ad4aaf24ca7?w=800&h=600&fit=crop",
    timezone: "America/New_York"
  },
  {
    id: "8",
    title: "Startup Legal Clinic",
    host: "Mark Thompson",
    description: "Legal advice for startups, contracts, and intellectual property",
    availableSlots: 2,
    totalSlots: 5,
    duration: 60,
    price: 250,
    category: "Legal",
    rating: 4.7,
    image: "https://images.unsplash.com/photo-1605810230434-7631ac76ec81?w=800&h=600&fit=crop",
    timezone: "America/Los_Angeles"
  }
];

const Index = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { t } = useTranslation();
  const { isOffline, cachedEvents, cacheEvents } = usePWA();
  
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("popularity");
  const [filterCategory, setFilterCategory] = useState("all");
  const [hostFilter, setHostFilter] = useState("");
  const [dateRange, setDateRange] = useState<{ from?: Date; to?: Date }>({});
  const [currency, setCurrency] = useState<'USD' | 'INR'>('USD');

  // Handle invite link with pre-selected slot
  useEffect(() => {
    const slotId = searchParams.get('slot');
    if (slotId) {
      console.log('Pre-selected slot:', slotId);
      // Navigate to event with pre-selected slot
    }
  }, [searchParams]);

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      const eventsToUse = isOffline ? cachedEvents : mockEvents;
      setEvents(eventsToUse);
      setLoading(false);
      
      if (!isOffline) {
        cacheEvents(mockEvents);
      }
    }, 1500);
  }, [isOffline, cachedEvents, cacheEvents]);

  const filteredEvents = events.filter(event => {
    const matchesSearch = event.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         event.host.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === "all" || event.category.toLowerCase() === filterCategory;
    const matchesHost = !hostFilter || event.host.toLowerCase().includes(hostFilter.toLowerCase());
    
    return matchesSearch && matchesCategory && matchesHost;
  });

  const sortedEvents = [...filteredEvents].sort((a, b) => {
    switch (sortBy) {
      case "price":
        return a.price - b.price;
      case "duration":
        return a.duration - b.duration;
      case "availability":
        return b.availableSlots - a.availableSlots;
      default:
        return b.rating - a.rating;
    }
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      {/* Offline indicator */}
      {isOffline && (
        <div className="bg-yellow-500 text-white px-4 py-2 text-center">
          <Badge variant="secondary" className="bg-yellow-600 text-white">
            Offline Mode - Showing cached events
          </Badge>
        </div>
      )}

      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="absolute top-6 right-6 flex items-center gap-3">
            <LocaleSwitch />
            <CurrencySelector value={currency} onChange={setCurrency} />
            <ThemeToggle />
          </div>
          
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 animate-fade-in">
              {t('hero.title')}
            </h1>
            <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl mx-auto animate-fade-in">
              {t('hero.subtitle')}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in">
              <Button size="lg" className="bg-white text-indigo-600 hover:bg-gray-100 text-lg px-8 py-4 rounded-full font-semibold shadow-lg hover:shadow-xl transition-all duration-300">
                <Calendar className="mr-2 h-5 w-5" />
                {t('hero.browse')}
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                className="border-2 border-white text-white hover:bg-white hover:text-indigo-600 text-lg px-8 py-4 rounded-full font-semibold transition-all duration-300 bg-transparent"
                onClick={() => navigate('/create-event')}
              >
                <Users className="mr-2 h-5 w-5" />
                {t('hero.host')}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Global Search and Filter */}
        <GlobalSearch
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          sortBy={sortBy}
          setSortBy={setSortBy}
          filterCategory={filterCategory}
          setFilterCategory={setFilterCategory}
          hostFilter={hostFilter}
          setHostFilter={setHostFilter}
          dateRange={dateRange}
          setDateRange={setDateRange}
        />

        {/* Results Summary */}
        {!loading && (
          <div className="mb-6">
            <p className="text-gray-600 dark:text-gray-300 text-lg">
              {sortedEvents.length} {t('events.found')}
              {searchTerm && ` ${t('events.for')} "${searchTerm}"`}
            </p>
          </div>
        )}

        {/* Events Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 auto-rows-fr">
          {loading ? (
            Array.from({ length: 8 }).map((_, index) => (
              <SkeletonLoader key={index} />
            ))
          ) : (
            <>
              {sortedEvents.map((event, index) => (
                <div key={event.id} className="h-full">
                  <EventCard 
                    event={event} 
                    index={index}
                    currency={currency}
                  />
                </div>
              ))}
              <div className="h-full">
                <AddEventCard />
              </div>
            </>
          )}
        </div>

        {/* Empty State */}
        {!loading && sortedEvents.length === 0 && (
          <div className="text-center py-16">
            <div className="w-24 h-24 mx-auto mb-6 bg-gray-100 dark:bg-slate-700 rounded-full flex items-center justify-center">
              <Calendar className="h-12 w-12 text-gray-400" />
            </div>
            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">{t('events.noResults')}</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-6">{t('events.noResultsDesc')}</p>
            <Button onClick={() => {setSearchTerm(""); setFilterCategory("all"); setHostFilter(""); setDateRange({});}}>
              {t('button.clearFilters')}
            </Button>
          </div>
        )}
      </div>

      <AnalyticsOptIn />
    </div>
  );
};

export default Index;
