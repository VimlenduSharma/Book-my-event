import { Edit, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useTranslation } from 'react-i18next';

interface AdminBannerProps {
  eventId: string;
  onEdit: () => void;
  onDelete: () => void;
}

const AdminBanner = ({ eventId, onEdit, onDelete }: AdminBannerProps) => {
  const { t } = useTranslation();

  return (
    <Alert className="mb-6 bg-blue-50 border-blue-200">
      <AlertDescription>
        <div className="flex items-center justify-between">
          <span className="text-blue-800 font-medium">
            You are viewing your own event as the creator
          </span>
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={onEdit}>
              <Edit className="h-4 w-4 mr-1" />
              {t('admin.edit')}
            </Button>
            <Button size="sm" variant="destructive" onClick={onDelete}>
              <Trash2 className="h-4 w-4 mr-1" />
              {t('admin.delete')}
            </Button>
          </div>
        </div>
      </AlertDescription>
    </Alert>
  );
};

export default AdminBanner;
