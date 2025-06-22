import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      "hero.title": "Schedule Your Success",
      "hero.subtitle": "Connect with industry experts, book consultations, and accelerate your growth",
      "hero.browse": "Browse Events",
      "hero.host": "Host an Event",
      "search.placeholder": "Search events or hosts...",
      "filter.category": "Category",
      "filter.all": "All Categories",
      "sort.by": "Sort by",
      "sort.popularity": "Popularity",
      "sort.price": "Price",
      "sort.duration": "Duration",
      "sort.availability": "Availability",
      "events.found": "event(s) found",
      "events.for": "for",
      "events.noResults": "No events found",
      "events.noResultsDesc": "Try adjusting your search or filter criteria",
      "button.clearFilters": "Clear Filters",
      "button.bookNow": "Book Now",
      "button.addMore": "Add More Events...",
      "card.free": "Free",
      "card.slotsLeft": "slots left",
      "card.slotLeft": "slot left",
      "card.fullyBooked": "Fully booked",
      "admin.edit": "Edit Event",
      "admin.delete": "Delete Event"
    }
  },
  hi: {
    translation: {
      "hero.title": "अपनी सफलता को शेड्यूल करें",
      "hero.subtitle": "उद्योग विशेषज्ञों से जुड़ें, परामर्श बुक करें, और अपनी वृद्धि को तेज़ करें",
      "hero.browse": "इवेंट्स देखें",
      "hero.host": "एक इवेंट होस्ट करें",
      "search.placeholder": "इवेंट या होस्ट खोजें...",
      "filter.category": "श्रेणी",
      "filter.all": "सभी श्रेणियां",
      "sort.by": "क्रमबद्ध करें",
      "sort.popularity": "लोकप्रियता",
      "sort.price": "मूल्य",
      "sort.duration": "अवधि",
      "sort.availability": "उपलब्धता",
      "events.found": "इवेंट मिले",
      "events.for": "के लिए",
      "events.noResults": "कोई इवेंट नहीं मिला",
      "events.noResultsDesc": "अपने खोज या फ़िल्टर मानदंडों को समायोजित करने का प्रयास करें",
      "button.clearFilters": "फ़िल्टर साफ़ करें",
      "button.bookNow": "अभी बुक करें",
      "button.addMore": "और इवेंट्स जोड़ें...",
      "card.free": "मुफ्त",
      "card.slotsLeft": "स्लॉट बचे हैं",
      "card.slotLeft": "स्लॉट बचा है",
      "card.fullyBooked": "पूरी तरह बुक",
      "admin.edit": "इवेंट संपादित करें",
      "admin.delete": "इवेंट हटाएं"
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'en',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
