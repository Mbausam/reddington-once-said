import { useState, useEffect, useRef } from 'react';
import { getFeaturedQuote, getRandomQuote } from '../api';

const HERO_IMAGES = [
    '/images/reddington-1.png',
    '/images/reddington-2.png',
    '/images/reddington-3.png',
    '/images/reddington-4.png',
    '/images/reddington-5.png',
];

const CYCLE_INTERVAL = 6000; // 6 seconds per image
const QUOTE_CYCLE_INTERVAL = 10000; // 10 seconds per quote

export default function HeroSection({ onScrollDown }) {
    const [currentQuote, setCurrentQuote] = useState(null);
    const [quoteFading, setQuoteFading] = useState(false);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);
    const [nextImageIndex, setNextImageIndex] = useState(1);
    const [transitioning, setTransitioning] = useState(false);
    const [titleRevealed, setTitleRevealed] = useState(false);
    const intervalRef = useRef(null);
    const quoteIntervalRef = useRef(null);

    // Load initial featured quote
    useEffect(() => {
        getFeaturedQuote()
            .then(setCurrentQuote)
            .catch(console.error);

        // Trigger title reveal animation after mount
        setTimeout(() => setTitleRevealed(true), 300);
    }, []);

    // Cycle quotes
    useEffect(() => {
        quoteIntervalRef.current = setInterval(async () => {
            setQuoteFading(true);
            try {
                const newQuote = await getRandomQuote();
                setTimeout(() => {
                    setCurrentQuote(newQuote);
                    setQuoteFading(false);
                }, 600); // Wait for fade-out before swapping
            } catch (err) {
                console.error(err);
                setQuoteFading(false);
            }
        }, QUOTE_CYCLE_INTERVAL);

        return () => clearInterval(quoteIntervalRef.current);
    }, []);

    // Rotate images with crossfade
    useEffect(() => {
        intervalRef.current = setInterval(() => {
            setTransitioning(true);

            setTimeout(() => {
                setCurrentImageIndex((prev) => (prev + 1) % HERO_IMAGES.length);
                setNextImageIndex((prev) => (prev + 1) % HERO_IMAGES.length);
                setTransitioning(false);
            }, 1200);
        }, CYCLE_INTERVAL);

        return () => clearInterval(intervalRef.current);
    }, []);

    const formatMeta = (q) => {
        if (!q) return '';
        const parts = [];
        if (q.season) parts.push(`Season ${q.season}`);
        if (q.episode) parts.push(`Episode ${q.episode}`);
        if (q.episode_title) parts.push(q.episode_title);
        return parts.join(' · ');
    };

    // Split title words for staggered animation
    const titleLine1 = 'Reddington';
    const titleLine2 = 'Once Said';

    return (
        <section className="hero" id="hero">
            <div className="hero__bg">
                <img
                    key={`current-${currentImageIndex}`}
                    src={HERO_IMAGES[currentImageIndex]}
                    alt="Raymond Reddington"
                    className={`hero__bg-img ${transitioning ? 'hero__bg-img--fading' : 'hero__bg-img--active'}`}
                />
                <img
                    key={`next-${nextImageIndex}`}
                    src={HERO_IMAGES[nextImageIndex]}
                    alt="Raymond Reddington"
                    className={`hero__bg-img ${transitioning ? 'hero__bg-img--active' : 'hero__bg-img--hidden'}`}
                />
            </div>
            <div className="hero__overlay" />
            <div className="hero__grain" />

            <div className="hero__content">
                <div className="hero__badge">
                    <span className="hero__badge-dot" />
                    The Blacklist · Quote Compendium
                </div>

                <h1 className={`hero__title ${titleRevealed ? 'hero__title--revealed' : ''}`}>
                    <span className="hero__title-line">
                        {titleLine1.split('').map((char, i) => (
                            <span
                                key={`l1-${i}`}
                                className="hero__title-char"
                                style={{ animationDelay: `${i * 0.06}s` }}
                            >
                                {char}
                            </span>
                        ))}
                    </span>
                    <br />
                    <span className="hero__title-line hero__title-line--gold">
                        {titleLine2.split('').map((char, i) => (
                            <span
                                key={`l2-${i}`}
                                className="hero__title-char"
                                style={{ animationDelay: `${(titleLine1.length + i) * 0.06 + 0.2}s` }}
                            >
                                {char === ' ' ? '\u00A0' : char}
                            </span>
                        ))}
                    </span>
                </h1>

                <div className={`hero__quote-wrapper ${quoteFading ? 'hero__quote-wrapper--fading' : ''}`}>
                    {currentQuote ? (
                        <>
                            <p className="hero__quote">{currentQuote.quote}</p>
                            <p className="hero__meta">{formatMeta(currentQuote)}</p>
                        </>
                    ) : (
                        <p className="hero__quote">Loading today's wisdom...</p>
                    )}
                </div>

                <button
                    className="hero__cta"
                    onClick={onScrollDown}
                    id="hero-cta"
                >
                    🎲 Deal Me a Quote
                </button>
            </div>

            <div className="hero__image-dots">
                {HERO_IMAGES.map((_, i) => (
                    <span
                        key={i}
                        className={`hero__image-dot ${i === currentImageIndex ? 'active' : ''}`}
                    />
                ))}
            </div>

            <div className="hero__scroll-indicator">
                <span />
            </div>
        </section>
    );
}
