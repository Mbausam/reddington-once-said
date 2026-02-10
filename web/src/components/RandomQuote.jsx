import { useState, useRef } from 'react';
import { getRandomQuote } from '../api';
import QuoteCard from './QuoteCard';

export default function RandomQuote() {
    const [quote, setQuote] = useState(null);
    const [loading, setLoading] = useState(false);
    const [flipping, setFlipping] = useState(false);
    const cardRef = useRef(null);

    const handleDeal = async () => {
        if (loading) return;
        setLoading(true);

        // Start flip-out animation
        setFlipping(true);

        try {
            const newQuote = await getRandomQuote();

            // Wait for flip-out to finish
            setTimeout(() => {
                setQuote(newQuote);
                setFlipping(false);
                setLoading(false);
            }, 350);
        } catch (err) {
            console.error('Failed to get quote:', err);
            setFlipping(false);
            setLoading(false);
        }
    };

    return (
        <section className="random-section section" id="random">
            <div className="container">
                <div className="section-title">
                    <h2>
                        Deal Me a Quote
                    </h2>
                    <p>Click the button. Let Red speak.</p>
                </div>

                <div className="random__display">
                    <div className="random__card-wrapper">
                        {quote ? (
                            <div
                                ref={cardRef}
                                className={`random__card ${flipping ? 'flipping' : 'revealed'}`}
                            >
                                <QuoteCard quote={quote} />
                            </div>
                        ) : (
                            <div className="search__empty" style={{ opacity: 0.5 }}>
                                <div className="search__empty-icon">🃏</div>
                                <p>Hit the button below to deal your first quote</p>
                            </div>
                        )}
                    </div>

                    <button
                        className="random__btn"
                        onClick={handleDeal}
                        disabled={loading}
                        id="deal-btn"
                    >
                        <span className="random__btn-icon">🎲</span>
                        {loading ? 'Dealing...' : quote ? 'Deal Again' : 'Deal Me a Quote'}
                    </button>
                </div>
            </div>
        </section>
    );
}
