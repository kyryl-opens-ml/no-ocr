// Feature component for highlighting key RAG and ColPali-based capabilities.
import { LucideIcon } from 'lucide-react';

interface FeatureProps {
  icon: LucideIcon;  // Lucide icon component to represent the feature
  title: string;     // Feature name/title
  description: string; // Feature description supporting markdown
}

export function Feature({ icon: Icon, title, description }: FeatureProps) {
  return (
    <div className="flex flex-col">
      <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-gray-900">
        <Icon className="h-5 w-5 flex-none text-blue-600" aria-hidden="true" />
        {title}
      </dt>
      <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-gray-600">
        <p className="flex-auto">{description}</p>
      </dd>
    </div>
  );
}