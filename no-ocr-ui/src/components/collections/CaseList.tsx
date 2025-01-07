import { useEffect, useState } from 'react';
import { Case } from '../../types/collection';
import { CaseCard } from './CaseCard';
import { LoadingSpinner } from '../shared/LoadingSpinner';
import { EmptyState } from '../shared/EmptyState';
import { noOcrApiUrl } from '../../config/api';
import { useAuthStore } from '../../stores/authStore';

export function CaseList() {
  const [cases, setCases] = useState<Case[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    async function fetchCases() {
      if (!user) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch(`${noOcrApiUrl}/get_cases?user_id=${user.id}`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        setCases(data.cases || []);
      } catch (error) {
        console.error('Error fetching cases:', error);
      } finally {
        setIsLoading(false);
      }
    }

    fetchCases();
  }, [user]);

  if (isLoading) return <LoadingSpinner />;

  if (cases.length === 0) {
    return (
      <EmptyState
        title="No cases yet"
        description="Get started by creating your first case"
        actionLink="/create-case"
        actionText="Create Case"
      />
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {cases.map((caseItem) => (
        <CaseCard key={caseItem.name} caseItem={caseItem} />
      ))}
    </div>
  );
}