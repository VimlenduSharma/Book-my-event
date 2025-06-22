import { useState } from "react";
import { Search, Filter, Calendar } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import { format } from "date-fns";
import { useTranslation } from 'react-i18next';

interface GlobalSearchProps {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  sortBy: string;
  setSortBy: (sort: string) => void;
  filterCategory: string;
  setFilterCategory: (category: string) => void;
  hostFilter: string;
  setHostFilter: (host: string) => void;
  dateRange: { from?: Date; to?: Date };
  setDateRange: (range: { from?: Date; to?: Date }) => void;
}

const GlobalSearch = ({
  searchTerm,
  setSearchTerm,
  sortBy,
  setSortBy,
  filterCategory,
  setFilterCategory,
  hostFilter,
  setHostFilter,
  dateRange,
  setDateRange
}: GlobalSearchProps) => {
  const { t } = useTranslation();
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl p-6 mb-8 border border-gray-100 dark:border-slate-700">
      <div className="flex flex-col lg:flex-row gap-4 items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <Input
            placeholder={t('search.placeholder')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 h-12 text-lg border-gray-200 focus:border-indigo-500 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700"
          />
        </div>
        
        <div className="flex gap-3 items-center">
          <Button
            variant="outline"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="h-12"
          >
            <Filter className="h-5 w-5 mr-2" />
            Advanced
          </Button>

          <div className="flex items-center gap-2">
            <Filter className="h-5 w-5 text-gray-500" />
            <Select value={filterCategory} onValueChange={setFilterCategory}>
              <SelectTrigger className="w-40 h-12 dark:border-slate-600 dark:bg-slate-700">
                <SelectValue placeholder={t('filter.category')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('filter.all')}</SelectItem>
                <SelectItem value="business">Business</SelectItem>
                <SelectItem value="technology">Technology</SelectItem>
                <SelectItem value="design">Design</SelectItem>
                <SelectItem value="marketing">Marketing</SelectItem>
                <SelectItem value="career">Career</SelectItem>
                <SelectItem value="legal">Legal</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-40 h-12 dark:border-slate-600 dark:bg-slate-700">
              <SelectValue placeholder={t('sort.by')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="popularity">{t('sort.popularity')}</SelectItem>
              <SelectItem value="price">{t('sort.price')}</SelectItem>
              <SelectItem value="duration">{t('sort.duration')}</SelectItem>
              <SelectItem value="availability">{t('sort.availability')}</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {showAdvanced && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-slate-600">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Filter by Host</label>
              <Input
                placeholder="Host name..."
                value={hostFilter}
                onChange={(e) => setHostFilter(e.target.value)}
                className="h-10"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Date Range</label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" className="h-10 w-full justify-start">
                    <Calendar className="mr-2 h-4 w-4" />
                    {dateRange.from ? (
                      dateRange.to ? (
                        `${format(dateRange.from, "MMM dd")} - ${format(dateRange.to, "MMM dd")}`
                      ) : (
                        format(dateRange.from, "MMM dd, yyyy")
                      )
                    ) : (
                      "Pick a date range"
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <CalendarComponent
                    mode="range"
                    selected={{ from: dateRange.from, to: dateRange.to }}
                    onSelect={(range) => setDateRange(range || {})}
                    numberOfMonths={2}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>

            <div className="flex items-end">
              <Button
                variant="outline"
                onClick={() => {
                  setHostFilter("");
                  setDateRange({});
                  setSearchTerm("");
                  setFilterCategory("all");
                }}
                className="h-10"
              >
                Clear All
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GlobalSearch;
