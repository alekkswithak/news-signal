import { ArticleSearchResult, AnalyzedArticle } from "../types";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed: ${res.status}`);
  }

  return res.json();
}

export const api = {
  search: (query: string) =>
    request<ArticleSearchResult[]>(`/api/articles/search?q=${encodeURIComponent(query)}`),

  analyze: (article: {
    url: string;
    title: string;
    description: string | null;
    source: string | null;
    published_at: string | null;
  }) =>
    request<AnalyzedArticle>("/api/articles/analyze", {
      method: "POST",
      body: JSON.stringify(article),
    }),

  history: () => request<AnalyzedArticle[]>("/api/articles/history"),
};
