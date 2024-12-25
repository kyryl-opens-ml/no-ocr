import { Case } from '../../types/collection';

interface CaseSelectProps {
  cases: Case[];
  selectedCase: string;
  onCaseChange: (caseId: string) => void;
}

export function CaseSelect({
  cases,
  selectedCase,
  onCaseChange,
}: CaseSelectProps) {
  return (
    <div>
      <label htmlFor="case" className="block text-sm font-medium text-gray-700">
        Select Case
      </label>
      <select
        id="case"
        value={selectedCase}
        onChange={(e) => onCaseChange(e.target.value)}
        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        required
      >
        <option value="">Select a case</option>
        {cases.map((caseItem) => (
          <option key={caseItem.id} value={caseItem.id}>
            {caseItem.name}
          </option>
        ))}
      </select>
    </div>
  );
}