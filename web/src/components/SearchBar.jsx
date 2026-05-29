import { useState, useEffect, useRef } from 'react';
import { searchQuotes, getFilteredQuotes, getThemes, getCharacters } from '../api';
import QuoteCard from './QuoteCard';

const QUOTE_TYPES = ['one-liner', 'monologue', 'parable', 'threat', 'wisdom', 'humor', 'emotional'];

export default function SearchBar() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [hasSearched, setHasSearched] = useState(false);
    const [filtersOpen, setFiltersOpen] = useState(false);
    const [activeFilters, setActiveFilters] = useState({});
    const [themeList, setThemeList] = useState([]);
    const [characterList, setCharacterList] = useState([]);
    const debounceRef = useRef(null);

    useEffect(() => {
        getThemes().then(d => setThemeList(Object.keys(d.themes || {}))).catch(() => {});
        getCharacters().then(d => setCharacterList((d.characters || []).map(c => c.name))).catch(() => {});
    }, []);

    useEffect(() => {
        if (debounceRef.current) clearTimeout(debounceRef.current);

        const hasText = query.length >= 3;
        const hasFilters = Object.keys(activeFilters).length > 0;

        if (!hasText && !hasFilters) {
            setResults([]);
            setHasSearched(false);
            return;
        }

        debounceRef.current = setTimeout(async () => {
            setLoading(true);
            try {
                let data;
                if (hasText) {
                    data = await searchQuotes(query);
                    // Apply client-side filters on top of text search
                    if (hasFilters) {
                        data = data.filter(q => {
                            if (activeFilters.theme && !(q.themes || []).some(t => t.toLowerCase() === activeFilters.theme.toLowerCase())) return false;
                            if (activeFilters.character && (q.character_addressed || '').toLowerCase() !== activeFilters.character.toLowerCase()) return false;
                            if (activeFilters.quote_type && q.quote_type !== activeFilters.quote_type) return false;
                            if (activeFilters.min_rating && (q.iconic_rating || 0) < activeFilters.min_rating) return false;
                            return true;
                        });
                    }
                } else {
                    data = await getFilteredQuotes(activeFilters);
                }
                setResults(data);
                setHasSearched(true);
            } catch (err) {
                console.error('Search failed:', err);
            } finally {
                setLoading(false);
            }
        }, 350);

        return () => {
            if (debounceRef.current) clearTimeout(debounceRef.current);
        };
    }, [query, activeFilters]);

    const toggleFilter = (key, value) => {
        setActiveFilters(prev => {
            const next = { ...prev };
            if (next[key] === value) {
                delete next[key];
            } else {
                next[key] = value;
            }
            return next;
        });
    };

    const clearFilters = () => setActiveFilters({});

    const activeCount = Object.keys(activeFilters).length;

    return (
        <section className="search-section section" id="search">
            <div className="container">
                <div className="section-title">
                    <h2>Search the Archives</h2>
                    <p>Find that quote you're thinking of. Just start typing.</p>
                </div>

                <div className="search__input-wrapper">
                    <span className="search__icon">🔍</span>
                    <input
                        type="text"
                        className="search__input"
                        placeholder='Try "revenge", "loyalty", or "darkness"...'
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                </div>

                <div className="search__filters">
                    <button
                        className={`search__filter-toggle ${filtersOpen ? 'search__filter-toggle--open' : ''} ${activeCount > 0 ? 'search__filter-toggle--active' : ''}`}
                        onClick={() => setFiltersOpen(!filtersOpen)}
                    >
                        🎯 Filters{activeCount > 0 ? ` (${activeCount})` : ''}
                    </button>
                    {activeCount > 0 && (
                        <button className="search__filter-clear" onClick={clearFilters}>
                            Clear all
                        </button>
                    )}
                </div>

                {filtersOpen && (
                    <div className="search__filter-panel">
                        <div className="search__filter-group">
                            <label>Theme</label>
                            <div className="search__filter-chips">
                                {themeList.slice(0, 12).map(t => (
                                    <button
                                        key={t}
                                        className={`search__filter-chip ${activeFilters.theme === t ? 'search__filter-chip--active' : ''}`}
                                        onClick={() => toggleFilter('theme', t)}
                                    >
                                        {t}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="search__filter-group">
                            <label>Character</label>
                            <div className="search__filter-chips">
                                {characterList.slice(0, 8).map(c => (
                                    <button
                                        key={c}
                                        className={`search__filter-chip ${activeFilters.character === c ? 'search__filter-chip--active' : ''}`}
                                        onClick={() => toggleFilter('character', c)}
                                    >
                                        {c}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="search__filter-row">
                            <div className="search__filter-group">
                                <label>Quote Type</label>
                                <select
                                    className="search__filter-select"
                                    value={activeFilters.quote_type || ''}
                                    onChange={(e) => {
                                        if (e.target.value) {
                                            setActiveFilters(prev => ({ ...prev, quote_type: e.target.value }));
                                        } else {
                                            setActiveFilters(prev => { const n = { ...prev }; delete n.quote_type; return n; });
                                        }
                                    }}
                                >
                                    <option value="">All types</option>
                                    {QUOTE_TYPES.map(t => (
                                        <option key={t} value={t}>{t}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="search__filter-group">
                                <label>Min Rating</label>
                                <div className="search__filter-stars">
                                    {[4, 3, 2, 1].map(r => (
                                        <button
                                            key={r}
                                            className={`search__filter-star ${activeFilters.min_rating === r ? 'search__filter-star--active' : ''}`}
                                            onClick={() => toggleFilter('min_rating', r)}
                                        >
                                            {r}+ ★
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {loading && (
                    <div className="loading">
                        <div className="loading__dots">
                            <span className="loading__dot" />
                            <span className="loading__dot" />
                            <span className="loading__dot" />
                        </div>
                    </div>
                )}

                {hasSearched && !loading && (
                    <>
                        <p className="search__count">
                            {results.length} quote{results.length !== 1 ? 's' : ''} found
                        </p>
                        {results.length > 0 ? (
                            <div className="search__results">
                                {results.slice(0, 30).map((quote, i) => (
                                    <QuoteCard key={i} quote={quote} index={i} />
                                ))}
                            </div>
                        ) : (
                            <div className="search__empty">
                                <div className="search__empty-icon">🕵️</div>
                                <p>No quotes matched. Even Reddington doesn't have words for everything.</p>
                            </div>
                        )}
                    </>
                )}
            </div>
        </section>
    );
}
