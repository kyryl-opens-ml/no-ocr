import { Loader2 } from 'lucide-react';

interface UploadProgressProps {
  progress: number;
  isUploading: boolean;
}

export function UploadProgress({ progress, isUploading }: UploadProgressProps) {
  if (!isUploading) return null;

  return (
    <div className="space-y-2">
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
      <div className="flex items-center justify-center text-sm text-gray-600">
        <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5" />
        Processing...
      </div>
    </div>
  );
}