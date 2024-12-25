import React, { useState } from 'react';
import { Upload, Loader2 } from 'lucide-react';
import { noOcrApiUrl } from '../config/api';

export default function CreateCase() {
  const [caseName, setCaseName] = useState('');
  const [files, setFiles] = useState<FileList | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [apiMessage, setApiMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!files || !caseName) return;

    setIsUploading(true);
    
    // Simulated upload progress
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 95) {
          clearInterval(interval);
          return prev;
        }
        return prev + 5;
      });
    }, 500);

    try {
      const formData = new FormData();
      formData.append('case_name', caseName);
      Array.from(files).forEach(file => formData.append('files', file));

      const response = await fetch(`${noOcrApiUrl}/create_case`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const result = await response.json();
      console.log('Upload successful:', result);
      setApiMessage(`Upload successful: ${JSON.stringify(result)}`);

      setUploadProgress(100);
      setTimeout(() => {
        setIsUploading(false);
        setCaseName('');
        setFiles(null);
        setUploadProgress(0);
      }, 500);
    } catch (error: unknown) {
      if (error instanceof Error) {
        console.error('Upload failed:', error);
        setApiMessage(`Upload failed: ${error.message}`);
      } else {
        console.error('Upload failed:', error);
        setApiMessage('Upload failed: An unknown error occurred.');
      }
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-10 p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Create New Case</h1>
      
      <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow-md">
        <div>
          <label htmlFor="case-name" className="block text-sm font-medium text-gray-700 mb-2">
            Case Name
          </label>
          <input
            type="text"
            id="case-name"
            value={caseName}
            onChange={(e) => setCaseName(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2"
            placeholder="Enter case name"
            required
          />
        </div>

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
                    onChange={(e) => setFiles(e.target.files)}
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

        {isUploading && (
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        )}

        <button
          type="submit"
          disabled={isUploading || !files || !caseName}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {isUploading ? (
            <>
              <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />
              Processing...
            </>
          ) : (
            'Create Case'
          )}
        </button>
      </form>

      {apiMessage && (
        <div className="mt-4 p-4 bg-gray-100 rounded-md">
          <p className="text-sm text-gray-700">{apiMessage}</p>
        </div>
      )}
    </div>
  );
}