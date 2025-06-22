import { useState } from "react";
import { format } from "date-fns";
import { Calendar, Clock, User, Mail, CreditCard, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Event, TimeSlot } from "@/types/Event";
import { useToast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const bookingSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email address"),
  notes: z.string().optional()
});

type BookingFormData = z.infer<typeof bookingSchema>;

interface BookingFormProps {
  event: Event;
  selectedSlot: TimeSlot | null;
  onSlotSelect: (slot: TimeSlot) => void;
}

const BookingForm = ({ event, selectedSlot }: BookingFormProps) => {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isBooked, setIsBooked] = useState(false);

  const { register, handleSubmit, formState: { errors, isValid } } = useForm<BookingFormData>({
    resolver: zodResolver(bookingSchema),
    mode: "onChange"
  });

  const onSubmit = async (data: BookingFormData) => {
    if (!selectedSlot) {
      toast({
        title: "Please select a time slot",
        description: "Choose an available time slot to proceed with booking.",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      setIsBooked(true);
      toast({
        title: "Booking confirmed! 🎉",
        description: "You'll receive a confirmation email shortly with meeting details.",
      });
      
      // Navigate to success page after a short delay
      setTimeout(() => {
        navigate('/success');
      }, 2000);
    }, 2000);
  };

  if (isBooked) {
    return (
      <Card className="shadow-xl border-0 bg-gradient-to-br from-green-50 to-emerald-50">
        <CardContent className="p-8 text-center">
          <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <Check className="h-8 w-8 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Booking Confirmed!</h3>
          <p className="text-gray-600 mb-6">
            Your session with {event.host} has been scheduled for{" "}
            {selectedSlot && format(new Date(selectedSlot.datetime), "EEEE, MMMM d 'at' h:mm a")}
          </p>
          <div className="bg-white rounded-lg p-4 border border-green-200">
            <p className="text-sm text-gray-600 mb-2">
              <strong>What's next?</strong>
            </p>
            <ul className="text-sm text-gray-600 space-y-1 text-left">
              <li>• Check your email for confirmation and meeting link</li>
              <li>• Add the event to your calendar</li>
              <li>• Prepare any questions or materials</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-xl border-0 sticky top-8">
      <CardHeader className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-t-lg">
        <CardTitle className="flex items-center gap-2">
          <Calendar className="h-5 w-5" />
          Book Your Session
        </CardTitle>
        {event.price > 0 && (
          <p className="text-white/90 font-semibold text-lg">
            ${event.price} per session
          </p>
        )}
      </CardHeader>

      <CardContent className="p-6">
        {selectedSlot ? (
          <div className="bg-indigo-50 rounded-lg p-4 mb-6 border border-indigo-200">
            <div className="flex items-center gap-2 text-indigo-700 mb-2">
              <Clock className="h-4 w-4" />
              <span className="font-medium">Selected Time</span>
            </div>
            <p className="text-indigo-900 font-semibold">
              {format(new Date(selectedSlot.datetime), "EEEE, MMMM d")}
            </p>
            <p className="text-indigo-700">
              {format(new Date(selectedSlot.datetime), "h:mm a")} ({event.duration} minutes)
            </p>
          </div>
        ) : (
          <div className="bg-gray-50 rounded-lg p-4 mb-6 border border-gray-200">
            <p className="text-gray-600 text-center">
              Please select a time slot from the calendar above
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <Label htmlFor="name" className="flex items-center gap-2 text-gray-700 font-medium">
              <User className="h-4 w-4" />
              Full Name *
            </Label>
            <Input
              id="name"
              {...register("name")}
              placeholder="Enter your full name"
              className="mt-2 h-12 border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
            />
            {errors.name && (
              <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="email" className="flex items-center gap-2 text-gray-700 font-medium">
              <Mail className="h-4 w-4" />
              Email Address *
            </Label>
            <Input
              id="email"
              type="email"
              {...register("email")}
              placeholder="Enter your email address"
              className="mt-2 h-12 border-gray-200 focus:border-indigo-500 focus:ring-indigo-500"
            />
            {errors.email && (
              <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="notes" className="text-gray-700 font-medium">
              Additional Notes (Optional)
            </Label>
            <Textarea
              id="notes"
              {...register("notes")}
              placeholder="Any specific topics you'd like to discuss?"
              className="mt-2 border-gray-200 focus:border-indigo-500 focus:ring-indigo-500 min-h-[100px]"
            />
          </div>

          <Button
            type="submit"
            disabled={!selectedSlot || !isValid || isSubmitting}
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold py-4 text-lg rounded-lg transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Processing...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                {event.price > 0 ? <CreditCard className="h-5 w-5" /> : <Calendar className="h-5 w-5" />}
                {event.price > 0 ? `Pay $${event.price} & Book` : "Book Free Session"}
              </div>
            )}
          </Button>

          {event.price === 0 && (
            <p className="text-center text-sm text-gray-500">
              This is a free session. No payment required.
            </p>
          )}
        </form>
      </CardContent>
    </Card>
  );
};

export default BookingForm;
