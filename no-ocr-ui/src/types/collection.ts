export interface Collection {
  name: string;
  status: string;
  number_of_PDFs: number;
  files: string[];
}

export interface SearchResult {
  documentName: string;
  excerpt: string;
  relevanceScore: number;
  pageNumber: number;
}