import { BookOpen } from 'lucide-react';

export function HowItWorks() {
  return (
    <div className="bg-white py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:max-w-4xl">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
            How It Works
          </h2>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Our platform uses advanced natural language processing to understand the context of your search queries and find the most relevant information in your documents.
          </p>
          
          <div className="mt-16 space-y-20 lg:mt-20 lg:space-y-20">
            <article className="relative isolate flex flex-col gap-8 lg:flex-row">
              <div className="relative aspect-[16/9] sm:aspect-[2/1] lg:aspect-square lg:w-64 lg:shrink-0">
                <BookOpen className="absolute inset-0 h-full w-full text-gray-900" />
              </div>
              <div>
                <div className="flex items-center gap-x-4 text-xs">
                  <time dateTime="2024" className="text-gray-500">
                    Step 1
                  </time>
                </div>
                <div className="group relative max-w-xl">
                  <h3 className="mt-3 text-lg font-semibold leading-6 text-gray-900">
                    Upload Your Documents
                  </h3>
                  <p className="mt-5 text-sm leading-6 text-gray-600">
                    Start by creating a collection and uploading your PDF documents. Our system will process and index them for efficient searching.
                  </p>
                </div>
              </div>
            </article>
          </div>
        </div>
      </div>
    </div>
  );
}