// Use relative paths when served from same origin (production),
// or VITE_API_URL for separate dev server
const API_BASE = import.meta.env.VITE_API_URL || '';

export async function getRandomQuote() {
    const res = await fetch(`${API_BASE}/api/quotes/random`);
    if (!res.ok) throw new Error('Failed to fetch random quote');
    return res.json();
}

export async function getFeaturedQuote() {
    const res = await fetch(`${API_BASE}/api/quotes/featured`);
    if (!res.ok) throw new Error('Failed to fetch featured quote');
    return res.json();
}

export async function searchQuotes(query) {
    if (!query || query.length < 3) return [];
    const res = await fetch(`${API_BASE}/api/quotes/search?query=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error('Failed to search quotes');
    return res.json();
}

export async function getQuotesBySeason(season) {
    const res = await fetch(`${API_BASE}/api/quotes?season=${season}`);
    if (!res.ok) throw new Error('Failed to fetch season quotes');
    return res.json();
}

export async function getStats() {
    const res = await fetch(`${API_BASE}/api/quotes/stats`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
}

export async function getAllQuotes() {
    const res = await fetch(`${API_BASE}/api/quotes`);
    if (!res.ok) throw new Error('Failed to fetch quotes');
    return res.json();
}
