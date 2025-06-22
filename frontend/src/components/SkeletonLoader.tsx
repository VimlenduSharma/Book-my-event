import { Card, CardContent } from "@/components/ui/card";

const SkeletonLoader = () => {
  return (
    <Card className="overflow-hidden shadow-lg animate-pulse">
      <div className="aspect-[4/3] bg-gray-300"></div>
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="space-y-2">
            <div className="h-5 bg-gray-300 rounded-md w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded-md w-1/2"></div>
          </div>
          
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded-md w-full"></div>
            <div className="h-4 bg-gray-200 rounded-md w-2/3"></div>
          </div>

          <div className="flex justify-between">
            <div className="flex gap-4">
              <div className="h-4 bg-gray-200 rounded-md w-16"></div>
              <div className="h-4 bg-gray-200 rounded-md w-16"></div>
            </div>
            <div className="h-4 bg-gray-200 rounded-md w-12"></div>
          </div>

          <div className="h-12 bg-gray-300 rounded-lg w-full"></div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SkeletonLoader;
