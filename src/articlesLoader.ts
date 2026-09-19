import { marked } from 'marked';
import type { Article } from './types';

export interface ParsedArticle extends Article {
  htmlContent: string;
}

export function loadArticles(): ParsedArticle[] {
  const files = import.meta.glob('/src/content/articles/*.md', {
    query: '?raw',
    import: 'default',
    eager: true,
  }) as Record<string, string>;

  const articles: ParsedArticle[] = [];

  for (const path in files) {
    const rawContent = files[path];
    const filename = path.split('/').pop()?.replace('.md', '') || 'article';

    const frontmatterRegex = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/;
    const match = rawContent.match(frontmatterRegex);

    let title = filename;
    let date = 'Recent';
    let readTime = '5 min read';
    let tags: string[] = [];
    let excerpt = '';
    let markdownBody = rawContent;

    if (match) {
      const yamlBlock = match[1];
      markdownBody = match[2].trim();

      yamlBlock.split('\n').forEach((line) => {
        const colonIdx = line.indexOf(':');
        if (colonIdx !== -1) {
          const key = line.slice(0, colonIdx).trim();
          const val = line.slice(colonIdx + 1).trim();

          if (key === 'title') {
            title = val.replace(/^["']|["']$/g, '');
          } else if (key === 'date') {
            date = val.replace(/^["']|["']$/g, '');
          } else if (key === 'readTime') {
            readTime = val.replace(/^["']|["']$/g, '');
          } else if (key === 'excerpt') {
            excerpt = val.replace(/^["']|["']$/g, '');
          } else if (key === 'tags') {
            if (val.startsWith('[') && val.endsWith(']')) {
              tags = val
                .slice(1, -1)
                .split(',')
                .map((t) => t.trim().replace(/^["']|["']$/g, ''))
                .filter(Boolean);
            }
          }
        }
      });
    }

    if (!excerpt) {
      excerpt = markdownBody.slice(0, 160).replace(/[#*_`]/g, '') + '...';
    }

    const htmlContent = marked.parse(markdownBody) as string;

    articles.push({
      id: filename,
      title,
      date,
      readTime,
      tags,
      excerpt,
      content: markdownBody,
      htmlContent,
      slug: filename,
    });
  }

  // Sort by date descending
  return articles.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
}
