import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AlertCircle, ArrowLeft, Home, RefreshCw } from "lucide-react";

const Error = () => {
  const navigate = useNavigate();
  const [countdown, setCountdown] = useState(15);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          navigate('/');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-orange-50 to-yellow-100 flex items-center justify-center">
      <div className="max-w-md mx-auto px-4">
        <Card className="shadow-2xl border-0 overflow-hidden">
          <CardContent className="p-8 text-center">
            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-32 h-32 bg-red-100 rounded-full animate-pulse"></div>
              </div>
              <AlertCircle className="h-24 w-24 text-red-500 mx-auto relative z-10 animate-scale-in" />
            </div>

            <h1 className="text-3xl font-bold text-gray-900 mb-4 animate-fade-in">
              Oops! Something went wrong
            </h1>
            
            <p className="text-gray-600 mb-8 animate-fade-in">
              We encountered an error while processing your request. Don't worry, we'll redirect you back home.
            </p>

            <div className="space-y-4 animate-fade-in">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-500 mb-2">Auto-redirect in</p>
                <p className="text-2xl font-bold text-red-600">{countdown}s</p>
              </div>

              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => window.location.reload()}
                  className="flex-1"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => navigate(-1)}
                  className="flex-1"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Go Back
                </Button>
                <Button 
                  onClick={() => navigate('/')}
                  className="flex-1 bg-red-600 hover:bg-red-700"
                >
                  <Home className="h-4 w-4 mr-2" />
                  Home
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Error;
