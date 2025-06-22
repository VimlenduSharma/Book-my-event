import { useState, useEffect } from "react";
import { Globe } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface TimezoneSwitchProps {
  value: string;
  onChange: (timezone: string) => void;
}

const commonTimezones = [
  { value: "America/New_York", label: "Eastern Time (ET)", offset: "UTC-5/-4" },
  { value: "America/Chicago", label: "Central Time (CT)", offset: "UTC-6/-5" },
  { value: "America/Denver", label: "Mountain Time (MT)", offset: "UTC-7/-6" },
  { value: "America/Los_Angeles", label: "Pacific Time (PT)", offset: "UTC-8/-7" },
  { value: "Europe/London", label: "Greenwich Mean Time (GMT)", offset: "UTC+0/+1" },
  { value: "Europe/Paris", label: "Central European Time (CET)", offset: "UTC+1/+2" },
  { value: "Asia/Tokyo", label: "Japan Standard Time (JST)", offset: "UTC+9" },
  { value: "Asia/Shanghai", label: "China Standard Time (CST)", offset: "UTC+8" },
  { value: "Asia/Kolkata", label: "India Standard Time (IST)", offset: "UTC+5:30" },
  { value: "Australia/Sydney", label: "Australian Eastern Time (AET)", offset: "UTC+10/+11" },
];

const TimezoneSwitch = ({ value, onChange }: TimezoneSwitchProps) => {
  const [detectedTimezone, setDetectedTimezone] = useState<string>("");

  useEffect(() => {
    // Detect browser timezone
    const browserTz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    setDetectedTimezone(browserTz);

    // Load from localStorage or use browser timezone
    const savedTimezone = localStorage.getItem('selectedTimezone');
    if (savedTimezone) {
      onChange(savedTimezone);
    } else if (!value) {
      onChange(browserTz);
    }
  }, []);

  const handleTimezoneChange = (newTimezone: string) => {
    onChange(newTimezone);
    localStorage.setItem('selectedTimezone', newTimezone);
  };

  const getCurrentOffset = () => {
    const now = new Date();
    const offset = -now.getTimezoneOffset() / 60;
    const sign = offset >= 0 ? '+' : '';
    return `UTC${sign}${offset}`;
  };

  const selectedTimezone = commonTimezones.find(tz => tz.value === value);

  return (
    <div className="flex items-center gap-2">
      <Globe className="h-4 w-4 text-gray-500" />
      <Select value={value} onValueChange={handleTimezoneChange}>
        <SelectTrigger className="w-64">
          <SelectValue>
            {selectedTimezone ? (
              <span className="flex items-center justify-between w-full">
                <span>{selectedTimezone.label}</span>
                <span className="text-xs text-gray-500 ml-2">{selectedTimezone.offset}</span>
              </span>
            ) : (
              `Current Timezone (${getCurrentOffset()})`
            )}
          </SelectValue>
        </SelectTrigger>
        <SelectContent className="max-h-60">
          {commonTimezones.map(timezone => (
            <SelectItem key={timezone.value} value={timezone.value}>
              <div className="flex items-center justify-between w-full">
                <span>{timezone.label}</span>
                <span className="text-xs text-gray-500 ml-4">{timezone.offset}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};

export default TimezoneSwitch;
