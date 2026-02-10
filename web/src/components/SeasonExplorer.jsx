import { useState, useEffect } from 'react';
import { getStats, getQuotesBySeason } from '../api';
import QuoteCard from './QuoteCard';

export default function SeasonExplorer() {
    const [stats, setStats] = useState(null);
    const [activeSeason, setActiveSeason] = useState(null);
    const [seasonQuotes, setSeasonQuotes] = useState({});
    const [loadingSeason, setLoadingSeason] = useState(null);

    useEffect(() => {
        getStats()
            .then(setStats)
            .catch(console.error);
    }, []);

    const toggleSeason = async (season) => {
        if (activeSeason === season) {
            setActiveSeason(null);
            return;
        }

        setActiveSeason(season);

        // Load quotes for this season if not already cached
        if (!seasonQuotes[season]) {
            setLoadingSeason(season);
            try {
                const quotes = await getQuotesBySeason(season);
                setSeasonQuotes((prev) => ({ ...prev, [season]: quotes }));
            } catch (err) {
                console.error(`Failed to load season ${season}:`, err);
            } finally {
                setLoadingSeason(null);
            }
        }
    };

    if (!stats) {
        return (
            <section className="section" id="seasons">
                <div className="container">
                    <div className="loading">
                        <div className="loading__dots">
                            <span className="loading__dot" />
                            <span className="loading__dot" />
                            <span className="loading__dot" />
                        </div>
                    </div>
                </div>
            </section>
        );
    }

    const seasons = Object.entries(stats.seasons)
        .map(([num, count]) => ({ number: parseInt(num), count }))
        .sort((a, b) => a.number - b.number);

    return (
        <section className="section" id="seasons">
            <div className="container">
                <div className="section-title">
                    <h2>
                        Season Explorer
                    </h2>
                    <p>
                        {stats.total_quotes} quotes across {stats.total_seasons} seasons.
                        Click a season to explore.
                    </p>
                </div>

                <div className="seasons__grid">
                    {seasons.map((s) => (
                        <div
                            key={s.number}
                            className={`season-item ${activeSeason === s.number ? 'active' : ''}`}
                        >
                            <div
                                className="season-item__header"
                                onClick={() => toggleSeason(s.number)}
                                id={`season-${s.number}-header`}
                            >
                                <div className="season-item__info">
                                    <span className="season-item__number">S{String(s.number).padStart(2, '0')}</span>
                                    <span className="season-item__label">Season {s.number}</span>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                    <span className="season-item__count">{s.count}</span>
                                    <span className="season-item__toggle">▼</span>
                                </div>
                            </div>

                            <div className="season-item__body">
                                <div className="season-item__quotes">
                                    {loadingSeason === s.number && (
                                        <div className="loading">
                                            <div className="loading__dots">
                                                <span className="loading__dot" />
                                                <span className="loading__dot" />
                                                <span className="loading__dot" />
                                            </div>
                                        </div>
                                    )}
                                    {seasonQuotes[s.number]?.map((quote, i) => (
                                        <QuoteCard key={i} quote={quote} index={i} />
                                    ))}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
