export interface Collection {
  id: string;
  name: string;
  documentCount: number;
  createdAt: string;
}

export interface SearchResult {
  documentName: string;
  excerpt: string;
  relevanceScore: number;
  pageNumber: number;
}