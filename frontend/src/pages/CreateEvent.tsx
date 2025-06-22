import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { Calendar as CalendarIcon, Clock, Upload, ArrowLeft, ArrowRight, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";

interface EventFormData {
  title: string;
  description: string;
  category: string;
  duration: number;
  price: number;
  maxPerSlot: number;
  timezone: string;
  image?: string;
  slots: { date: Date; time: string }[];
}

const CreateEvent = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<EventFormData>({
    title: "",
    description: "",
    category: "",
    duration: 60,
    price: 0,
    maxPerSlot: 1,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    slots: []
  });

  const [selectedDate, setSelectedDate] = useState<Date>();
  const [selectedTime, setSelectedTime] = useState("");
  const [dragOver, setDragOver] = useState(false);

  const steps = [
    { id: 1, title: "Basics", description: "Event details" },
    { id: 2, title: "Slots", description: "Available times" },
    { id: 3, title: "Branding", description: "Image & final touches" }
  ];

  const timeSlots = [
    "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
    "15:00", "15:30", "16:00", "16:30", "17:00", "17:30"
  ];

  const handleNext = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const addTimeSlot = () => {
    if (selectedDate && selectedTime) {
      const newSlot = { date: selectedDate, time: selectedTime };
      const exists = formData.slots.some(slot => 
        slot.date.toDateString() === selectedDate.toDateString() && slot.time === selectedTime
      );
      
      if (!exists) {
        setFormData(prev => ({
          ...prev,
          slots: [...prev.slots, newSlot]
        }));
        setSelectedTime("");
      } else {
        toast({
          title: "Slot already exists",
          description: "This time slot has already been added.",
          variant: "destructive"
        });
      }
    }
  };

  const removeTimeSlot = (index: number) => {
    setFormData(prev => ({
      ...prev,
      slots: prev.slots.filter((_, i) => i !== index)
    }));
  };

  const addRepeatingSlots = () => {
    if (!selectedDate) return;
    
    const newSlots = timeSlots.map(time => ({ date: selectedDate, time }));
    const filteredSlots = newSlots.filter(newSlot => 
      !formData.slots.some(existingSlot => 
        existingSlot.date.toDateString() === newSlot.date.toDateString() && 
        existingSlot.time === newSlot.time
      )
    );
    
    setFormData(prev => ({
      ...prev,
      slots: [...prev.slots, ...filteredSlots]
    }));
  };

  const handleImageDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    const imageFile = files.find(file => file.type.startsWith('image/'));
    
    if (imageFile) {
      const reader = new FileReader();
      reader.onload = () => {
        setFormData(prev => ({ ...prev, image: reader.result as string }));
      };
      reader.readAsDataURL(imageFile);
    }
  };

  const handleSubmit = () => {
    if (!formData.title || !formData.description || formData.slots.length === 0) {
      toast({
        title: "Missing required fields",
        description: "Please fill in all required fields and add at least one time slot.",
        variant: "destructive"
      });
      return;
    }

    toast({
      title: "Event created successfully!",
      description: "Your event has been published and is now available for booking.",
    });
    
    navigate('/success');
  };

  const renderBasicsStep = () => (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="title">Event Title *</Label>
        <Input
          id="title"
          placeholder="e.g., Product Strategy Session"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description *</Label>
        <Textarea
          id="description"
          placeholder="Describe what participants can expect from this session..."
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          rows={4}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="category">Category</Label>
          <Select value={formData.category} onValueChange={(value) => setFormData(prev => ({ ...prev, category: value }))}>
            <SelectTrigger>
              <SelectValue placeholder="Select category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="business">Business</SelectItem>
              <SelectItem value="technology">Technology</SelectItem>
              <SelectItem value="design">Design</SelectItem>
              <SelectItem value="marketing">Marketing</SelectItem>
              <SelectItem value="career">Career</SelectItem>
              <SelectItem value="legal">Legal</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="duration">Duration (minutes)</Label>
          <Input
            id="duration"
            type="number"
            value={formData.duration}
            onChange={(e) => setFormData(prev => ({ ...prev, duration: parseInt(e.target.value) || 60 }))}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="price">Price ($)</Label>
          <Input
            id="price"
            type="number"
            placeholder="0 for free"
            value={formData.price}
            onChange={(e) => setFormData(prev => ({ ...prev, price: parseFloat(e.target.value) || 0 }))}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="maxPerSlot">Max attendees per slot</Label>
          <Input
            id="maxPerSlot"
            type="number"
            value={formData.maxPerSlot}
            onChange={(e) => setFormData(prev => ({ ...prev, maxPerSlot: parseInt(e.target.value) || 1 }))}
          />
        </div>
      </div>
    </div>
  );

  const renderSlotsStep = () => (
    <div className="space-y-6">
      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <Label>Select Date</Label>
          <Calendar
            mode="single"
            selected={selectedDate}
            onSelect={setSelectedDate}
            disabled={(date) => date < new Date()}
            className="rounded-md border"
          />
        </div>

        <div className="space-y-4">
          <Label>Select Time</Label>
          <div className="grid grid-cols-3 gap-2 max-h-60 overflow-y-auto">
            {timeSlots.map((time) => (
              <Button
                key={time}
                variant={selectedTime === time ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedTime(time)}
                className="text-xs"
              >
                {time}
              </Button>
            ))}
          </div>
          
          <div className="flex gap-2">
            <Button onClick={addTimeSlot} disabled={!selectedDate || !selectedTime} className="flex-1">
              <Clock className="h-4 w-4 mr-2" />
              Add Slot
            </Button>
            <Button variant="outline" onClick={addRepeatingSlots} disabled={!selectedDate}>
              Add All Times
            </Button>
          </div>
        </div>
      </div>

      {formData.slots.length > 0 && (
        <div className="space-y-2">
          <Label>Added Time Slots ({formData.slots.length})</Label>
          <div className="max-h-40 overflow-y-auto space-y-2">
            {formData.slots.map((slot, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="text-sm">
                  {format(slot.date, 'MMM d, yyyy')} at {slot.time}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => removeTimeSlot(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  Remove
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderBrandingStep = () => (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label>Event Image</Label>
        <div
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
            dragOver ? "border-indigo-500 bg-indigo-50" : "border-gray-300",
            formData.image ? "border-solid" : ""
          )}
          onDrop={handleImageDrop}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
        >
          {formData.image ? (
            <div className="space-y-4">
              <img src={formData.image} alt="Preview" className="max-h-40 mx-auto rounded" />
              <Button variant="outline" onClick={() => setFormData(prev => ({ ...prev, image: undefined }))}>
                Remove Image
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <Upload className="h-12 w-12 mx-auto text-gray-400" />
              <div>
                <p className="text-lg font-medium">Drop your image here</p>
                <p className="text-sm text-gray-500">or click to browse</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="font-semibold mb-2">Event Summary</h3>
        <div className="space-y-1 text-sm">
          <p><strong>Title:</strong> {formData.title || "Untitled Event"}</p>
          <p><strong>Category:</strong> {formData.category || "Uncategorized"}</p>
          <p><strong>Duration:</strong> {formData.duration} minutes</p>
          <p><strong>Price:</strong> {formData.price === 0 ? "Free" : `$${formData.price}`}</p>
          <p><strong>Time Slots:</strong> {formData.slots.length} slots added</p>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <Button variant="ghost" onClick={() => navigate('/')} className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Events
          </Button>
          
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Create New Event</h1>
          <p className="text-gray-600">Set up your event and start accepting bookings</p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={cn(
                "flex items-center justify-center w-10 h-10 rounded-full border-2 font-semibold",
                currentStep >= step.id
                  ? "bg-indigo-600 border-indigo-600 text-white"
                  : "border-gray-300 text-gray-500"
              )}>
                {currentStep > step.id ? <Check className="h-5 w-5" /> : step.id}
              </div>
              <div className="ml-2 mr-8">
                <p className={cn("font-medium", currentStep >= step.id ? "text-indigo-600" : "text-gray-500")}>
                  {step.title}
                </p>
                <p className="text-xs text-gray-500">{step.description}</p>
              </div>
              {index < steps.length - 1 && (
                <div className={cn(
                  "w-16 h-0.5 mr-8",
                  currentStep > step.id ? "bg-indigo-600" : "bg-gray-300"
                )} />
              )}
            </div>
          ))}
        </div>

        {/* Form Content */}
        <Card className="shadow-xl">
          <CardHeader>
            <CardTitle>
              Step {currentStep}: {steps[currentStep - 1].title}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {currentStep === 1 && renderBasicsStep()}
            {currentStep === 2 && renderSlotsStep()}
            {currentStep === 3 && renderBrandingStep()}
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <Button variant="outline" onClick={handlePrev} disabled={currentStep === 1}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Previous
          </Button>
          
          {currentStep < 3 ? (
            <Button onClick={handleNext}>
              Next
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          ) : (
            <Button onClick={handleSubmit} className="bg-indigo-600 hover:bg-indigo-700">
              Create Event
              <Check className="h-4 w-4 ml-2" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CreateEvent;
