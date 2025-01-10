import { CaseList } from './collections/CaseList';

export default function Cases() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Cases</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage your PDF cases and their contents
          </p>
        </div>
      </div>
      
      <div className="mt-8">
        <CaseList />
      </div>
    </div>
  );
}