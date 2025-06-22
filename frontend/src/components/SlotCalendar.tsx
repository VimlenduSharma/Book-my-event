import { useState } from "react";
import { Calendar, Clock, Grid, List } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import { format } from "date-fns";

interface TimeSlot {
  id: string;
  time: string;
  available: boolean;
  booked?: boolean;
}

interface SlotCalendarProps {
  eventId: string;
  duration: number;
  timezone: string;
  onSlotSelect: (slotId: string, date: Date, time: string) => void;
}

const SlotCalendar = ({ eventId, duration, timezone, onSlotSelect }: SlotCalendarProps) => {
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());
  const [viewMode, setViewMode] = useState<"grid" | "agenda">("grid");

  // Mock time slots for demonstration
  const timeSlots: TimeSlot[] = [
    { id: "1", time: "09:00", available: true },
    { id: "2", time: "10:00", available: true },
    { id: "3", time: "11:00", available: false, booked: true },
    { id: "4", time: "14:00", available: true },
    { id: "5", time: "15:00", available: true },
    { id: "6", time: "16:00", available: false, booked: true },
  ];

  const handleSlotClick = (slot: TimeSlot) => {
    if (slot.available && selectedDate) {
      onSlotSelect(slot.id, selectedDate, slot.time);
    }
  };

  const availableSlots = timeSlots.filter(slot => slot.available);
  const bookedSlots = timeSlots.filter(slot => slot.booked);

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Select Date & Time
          </CardTitle>
          <div className="flex gap-2">
            <Button
              variant={viewMode === "grid" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewMode("grid")}
            >
              <Grid className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === "agenda" ? "default" : "outline"}
              size="sm"
              onClick={() => setViewMode("agenda")}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <p className="text-sm text-muted-foreground">
          Duration: {duration} minutes • Timezone: {timezone}
        </p>
      </CardHeader>
      
      <CardContent className="space-y-6">
        <div className="flex flex-col md:flex-row gap-6">
          {/* Calendar */}
          <div className="flex-1">
            <CalendarComponent
              mode="single"
              selected={selectedDate}
              onSelect={setSelectedDate}
              disabled={(date) => date < new Date()}
              className="rounded-md border"
            />
          </div>

          {/* Time Slots */}
          <div className="flex-1">
            {selectedDate && (
              <div className="space-y-4">
                <h3 className="font-semibold">
                  Available times for {format(selectedDate, "MMMM d, yyyy")}
                </h3>
                
                {viewMode === "grid" ? (
                  <div className="grid grid-cols-2 gap-2">
                    {timeSlots.map((slot) => (
                      <Button
                        key={slot.id}
                        variant={slot.available ? "outline" : "secondary"}
                        disabled={!slot.available}
                        onClick={() => handleSlotClick(slot)}
                        className={`p-3 h-auto flex flex-col items-center gap-1 ${
                          slot.available 
                            ? "hover:bg-primary hover:text-primary-foreground" 
                            : "opacity-50"
                        }`}
                      >
                        <Clock className="h-4 w-4" />
                        <span className="text-sm font-medium">{slot.time}</span>
                        {slot.booked && (
                          <Badge variant="secondary" className="text-xs">
                            Booked
                          </Badge>
                        )}
                      </Button>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-2">
                    {timeSlots.map((slot) => (
                      <div
                        key={slot.id}
                        className={`flex items-center justify-between p-3 rounded-lg border ${
                          slot.available 
                            ? "border-border hover:bg-accent cursor-pointer" 
                            : "border-muted bg-muted/50"
                        }`}
                        onClick={() => slot.available && handleSlotClick(slot)}
                      >
                        <div className="flex items-center gap-3">
                          <Clock className="h-4 w-4" />
                          <span className="font-medium">{slot.time}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {slot.booked ? (
                            <Badge variant="secondary">Booked</Badge>
                          ) : (
                            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                              Available
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Summary */}
                <div className="pt-4 border-t">
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>{availableSlots.length} available</span>
                    <span>{bookedSlots.length} booked</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SlotCalendar;
