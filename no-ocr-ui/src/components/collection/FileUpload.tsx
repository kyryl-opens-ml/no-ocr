import { Upload } from 'lucide-react';

interface FileUploadProps {
  files: FileList | null;
  onFilesChange: (files: FileList | null) => void;
}

export function FileUpload({ files, onFilesChange }: FileUploadProps) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Upload PDFs
      </label>
      <div className="flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
        <div className="space-y-1 text-center">
          <Upload className="mx-auto h-12 w-12 text-gray-400" />
          <div className="flex text-sm text-gray-600">
            <label htmlFor="pdfs" className="relative cursor-pointer rounded-md bg-white font-medium text-blue-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2 hover:text-blue-500">
              <span>Upload PDFs</span>
              <input
                id="pdfs"
                type="file"
                className="sr-only"
                multiple
                accept=".pdf"
                onChange={(e) => onFilesChange(e.target.files)}
                required
              />
            </label>
            <p className="pl-1">or drag and drop</p>
          </div>
          <p className="text-xs text-gray-500">PDF files only</p>
        </div>
      </div>
      {files && (
        <div className="mt-2">
          <p className="text-sm text-gray-500">
            Selected {files.length} file(s)
          </p>
        </div>
      )}
    </div>
  );
}