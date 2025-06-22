import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { X, BarChart3 } from "lucide-react";

const AnalyticsOptIn = () => {
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    const hasOptedIn = localStorage.getItem('analytics-opted-in');
    const hasDeclined = localStorage.getItem('analytics-declined');
    
    if (!hasOptedIn && !hasDeclined) {
      setShowBanner(true);
    } else if (hasOptedIn === 'true') {
      // Initialize analytics
      initializeAnalytics();
    }
  }, []);

  const initializeAnalytics = () => {
    // Simple pageview tracker
    if (typeof window !== 'undefined') {
      console.log('Analytics: Page viewed', window.location.pathname);
      // Here you would integrate with Plausible, PostHog, etc.
    }
  };

  const handleOptIn = () => {
    localStorage.setItem('analytics-opted-in', 'true');
    setShowBanner(false);
    initializeAnalytics();
  };

  const handleDecline = () => {
    localStorage.setItem('analytics-declined', 'true');
    setShowBanner(false);
  };

  if (!showBanner) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 z-50 max-w-md mx-auto">
      <Card className="shadow-2xl border-indigo-200">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-sm">
              <BarChart3 className="h-4 w-4" />
              Help us improve
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDecline}
              className="h-6 w-6 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <p className="text-sm text-gray-600 mb-4">
            We'd like to collect anonymous analytics to improve your experience. No personal data is collected.
          </p>
          <div className="flex gap-2">
            <Button size="sm" onClick={handleOptIn} className="flex-1">
              Allow Analytics
            </Button>
            <Button size="sm" variant="outline" onClick={handleDecline} className="flex-1">
              No Thanks
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalyticsOptIn;
