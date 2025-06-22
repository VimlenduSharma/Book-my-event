import { DollarSign, IndianRupee } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface CurrencySelectorProps {
  value: 'USD' | 'INR';
  onChange: (currency: 'USD' | 'INR') => void;
}

const CurrencySelector = ({ value, onChange }: CurrencySelectorProps) => {
  return (
    <div className="flex items-center gap-2">
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="w-24">
          <SelectValue>
            <div className="flex items-center gap-1">
              {value === 'USD' ? (
                <DollarSign className="h-4 w-4" />
              ) : (
                <IndianRupee className="h-4 w-4" />
              )}
              <span>{value}</span>
            </div>
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="USD">
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              <span>USD</span>
            </div>
          </SelectItem>
          <SelectItem value="INR">
            <div className="flex items-center gap-2">
              <IndianRupee className="h-4 w-4" />
              <span>INR</span>
            </div>
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
};

export default CurrencySelector;
