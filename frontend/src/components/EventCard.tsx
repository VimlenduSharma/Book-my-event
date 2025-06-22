import { useState } from "react";
import { Clock, Users, Star, DollarSign, IndianRupee } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Event } from "@/types/Event";
import { Link } from "react-router-dom";
import { AspectRatio } from "@/components/ui/aspect-ratio";

interface EventCardProps {
  event: Event;
  index: number;
  currency?: 'USD' | 'INR';
}

const EventCard = ({ event, index, currency = 'USD' }: EventCardProps) => {
  const [imageLoaded, setImageLoaded] = useState(false);

  const getAvailabilityColor = (available: number, total: number) => {
    const percentage = (available / total) * 100;
    if (percentage > 50) return "bg-green-500";
    if (percentage > 20) return "bg-yellow-500";
    return "bg-red-500";
  };

  const getAvailabilityText = (available: number) => {
    if (available === 0) return "Fully booked";
    if (available === 1) return "1 slot left";
    return `${available} slots left`;
  };

  const formatPrice = (price: number) => {
    if (price === 0) return "Free";
    if (currency === 'INR') {
      return `₹${(price * 83).toFixed(0)}`; // Approximate USD to INR conversion
    }
    return `$${price}`;
  };

  const CurrencyIcon = currency === 'INR' ? IndianRupee : DollarSign;

  return (
    <Link to={`/event/${event.id}`} className="h-full">
      <Card 
        className="group hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 hover:scale-105 cursor-pointer border-0 shadow-lg overflow-hidden bg-white h-full flex flex-col"
        style={{
          animationDelay: `${index * 100}ms`,
        }}
      >
        <div className="relative overflow-hidden">
          <AspectRatio ratio={4/3}>
            <div className="w-full h-full bg-gradient-to-br from-indigo-100 to-purple-100">
              {event.image && (
                <img
                  src={event.image}
                  alt={event.title}
                  className={`w-full h-full object-cover transition-all duration-500 group-hover:scale-110 ${
                    imageLoaded ? 'opacity-100' : 'opacity-0'
                  }`}
                  onLoad={() => setImageLoaded(true)}
                />
              )}
            </div>
          </AspectRatio>
          
          {/* Overlays */}
          <div className="absolute top-3 left-3">
            <Badge 
              className={`${getAvailabilityColor(event.availableSlots, event.totalSlots)} text-white font-medium px-3 py-1`}
            >
              {getAvailabilityText(event.availableSlots)}
            </Badge>
          </div>

          <div className="absolute top-3 right-3">
            <Badge variant="secondary" className="bg-white/90 text-gray-800 font-medium">
              {event.category}
            </Badge>
          </div>

          {event.price > 0 && (
            <div className="absolute bottom-3 right-3">
              <Badge className="bg-green-600 text-white font-bold px-3 py-1">
                <CurrencyIcon className="h-3 w-3 mr-1" />
                {formatPrice(event.price)}
              </Badge>
            </div>
          )}
        </div>

        <CardContent className="p-6 flex-1 flex flex-col">
          <div className="space-y-4 flex-1 flex flex-col">
            <div>
              <h3 className="font-bold text-lg text-gray-900 group-hover:text-indigo-600 transition-colors line-clamp-2">
                {event.title}
              </h3>
              <p className="text-gray-600 font-medium mt-1">by {event.host}</p>
            </div>

            <p className="text-gray-600 text-sm line-clamp-2 leading-relaxed flex-1">
              {event.description}
            </p>

            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-1 text-gray-500">
                  <Clock className="h-4 w-4" />
                  <span>{event.duration}min</span>
                </div>
                <div className="flex items-center gap-1 text-gray-500">
                  <Users className="h-4 w-4" />
                  <span>{event.totalSlots}</span>
                </div>
              </div>
              
              <div className="flex items-center gap-1 text-yellow-500">
                <Star className="h-4 w-4 fill-current" />
                <span className="text-gray-700 font-medium">{event.rating}</span>
              </div>
            </div>

            <Button 
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold py-3 rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl mt-auto"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
              }}
            >
              Book Now
            </Button>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
};

export default EventCard;
