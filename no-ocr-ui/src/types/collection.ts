export interface Case {
  name: string;
  status: string;
  number_of_PDFs: number;
  files: string[];
  documentCount: number;
  createdAt: string;
  id: string;
}

export interface SearchResult {
  documentName: string;
  excerpt: string;
  relevanceScore: number;
  pageNumber: number;
}