import { useState, useEffect, useRef } from 'react';
import { searchQuotes } from '../api';
import QuoteCard from './QuoteCard';

export default function SearchBar() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [hasSearched, setHasSearched] = useState(false);
    const debounceRef = useRef(null);

    useEffect(() => {
        if (debounceRef.current) clearTimeout(debounceRef.current);

        if (query.length < 3) {
            setResults([]);
            setHasSearched(false);
            return;
        }

        debounceRef.current = setTimeout(async () => {
            setLoading(true);
            try {
                const data = await searchQuotes(query);
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
    }, [query]);

    return (
        <section className="search-section section" id="search">
            <div className="container">
                <div className="section-title">
                    <h2>
                        Search the Archives
                    </h2>
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
                        id="search-input"
                    />
                </div>

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
                                {results.slice(0, 20).map((quote, i) => (
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
