import { Plus } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { useTranslation } from 'react-i18next';

const AddEventCard = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <Card className="group hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 hover:scale-105 cursor-pointer border-2 border-dashed border-gray-300 bg-gray-50 hover:border-indigo-400 hover:bg-indigo-50 h-full flex flex-col">
      <CardContent className="p-6 h-full flex flex-col items-center justify-center flex-1">
        <div className="text-center space-y-4 flex flex-col items-center justify-center h-full">
          <div className="w-16 h-16 mx-auto bg-indigo-100 rounded-full flex items-center justify-center group-hover:bg-indigo-200 transition-colors">
            <Plus className="h-8 w-8 text-indigo-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-700 group-hover:text-indigo-700">
            {t('button.addMore')}
          </h3>
          <p className="text-sm text-gray-500 mb-4">
            Create and host your own events
          </p>
          <Button 
            onClick={() => navigate('/create-event')}
            className="bg-indigo-600 hover:bg-indigo-700 text-white mt-auto"
          >
            Create Event
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default AddEventCard;
