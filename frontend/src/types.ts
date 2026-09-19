export type TabType = 'home' | 'articles' | 'games' | 'info';

export interface Article {
  id: string;
  title: string;
  excerpt: string;
  content: string;
  date: string;
  readTime: string;
  tags: string[];
  slug: string;
}

export interface GameItem {
  id: string;
  title: string;
  genre: string;
  tech: string[];
  description: string;
  status: 'Ready to Compile' | 'In Development' | 'Concept';
  controls?: string[];
  features?: string[];
}
