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

export async function getFilteredQuotes({ season, theme, character, quote_type, min_rating } = {}) {
    const params = new URLSearchParams();
    if (season) params.set('season', season);
    if (theme) params.set('theme', theme);
    if (character) params.set('character', character);
    if (quote_type) params.set('quote_type', quote_type);
    if (min_rating) params.set('min_rating', min_rating);
    const qs = params.toString();
    const res = await fetch(`${API_BASE}/api/quotes${qs ? '?' + qs : ''}`);
    if (!res.ok) throw new Error('Failed to fetch filtered quotes');
    return res.json();
}

export async function getThemes() {
    const res = await fetch(`${API_BASE}/api/themes`);
    if (!res.ok) throw new Error('Failed to fetch themes');
    return res.json();
}

export async function getCharacters() {
    const res = await fetch(`${API_BASE}/api/characters`);
    if (!res.ok) throw new Error('Failed to fetch characters');
    return res.json();
}

export async function getTopQuotes(limit = 20) {
    const res = await fetch(`${API_BASE}/api/quotes/top?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch top quotes');
    return res.json();
}
