import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { I18nextProvider } from 'react-i18next';
import i18n from '@/i18n/i18n';
import Index from "./pages/Index";
import EventDetails from "./pages/EventDetails";
import CreateEvent from "./pages/CreateEvent";
import MyBookings from "./pages/MyBookings";
import Success from "./pages/Success";
import Error from "./pages/Error";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

// Initialize saved language
const savedLanguage = localStorage.getItem('language');
if (savedLanguage) {
  i18n.changeLanguage(savedLanguage);
}

const App = () => (
  <QueryClientProvider client={queryClient}>
    <I18nextProvider i18n={i18n}>
      <ThemeProvider>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/event/:id" element={<EventDetails />} />
              <Route path="/create-event" element={<CreateEvent />} />
              <Route path="/my-bookings" element={<MyBookings />} />
              <Route path="/success" element={<Success />} />
              <Route path="/error" element={<Error />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </ThemeProvider>
    </I18nextProvider>
  </QueryClientProvider>
);

export default App;
