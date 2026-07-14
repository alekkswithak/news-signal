import { ArticleSearchResult, AnalyzedArticle } from "../types";

// Relative "/api" paths work locally and behind the Docker/Nginx proxy.
// On Vercel, the frontend and backend are different domains, so
// VITE_API_URL points straight at the deployed Render backend.
const API_BASE = import.meta.env.VITE_API_URL ?? "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
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
