import { useState, useEffect } from 'react';
import { getTopQuotes } from '../api';
import QuoteCard from './QuoteCard';

export default function IconicHall() {
    const [quotes, setQuotes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getTopQuotes(20)
            .then((data) => {
                setQuotes(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    if (loading) {
        return (
            <section className="iconic-hall" id="iconic">
                <div className="container">
                    <h2 className="section-title">Red's Greatest Hits</h2>
                    <div className="iconic-hall__loading">
                        <span className="loading-dot" />
                        <span className="loading-dot" />
                        <span className="loading-dot" />
                    </div>
                </div>
            </section>
        );
    }

    if (quotes.length === 0) return null;

    return (
        <section className="iconic-hall" id="iconic">
            <div className="container">
                <h2 className="section-title">Red's Greatest Hits</h2>
                <p className="section-subtitle">The most iconic, unforgettable lines — rated 4+ by the TranscriptMiner</p>
                <div className="iconic-hall__grid">
                    {quotes.map((q, i) => (
                        <QuoteCard key={`top-${i}`} quote={q} index={i} />
                    ))}
                </div>
            </div>
        </section>
    );
}
