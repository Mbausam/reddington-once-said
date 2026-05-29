import { useState, useRef } from 'react';

const MAX_STARS = 5;

export default function QuoteCard({ quote, index = 0 }) {
    const [copied, setCopied] = useState(false);
    const [speaking, setSpeaking] = useState(false);
    const utteranceRef = useRef(null);

    const rating = quote.iconic_rating || 0;
    const themes = quote.themes || [];
    const character = quote.character_addressed;
    const quoteType = quote.quote_type;

    const formatBadge = () => {
        const parts = [];
        if (quote.season) parts.push(`S${String(quote.season).padStart(2, '0')}`);
        if (quote.episode) parts.push(`E${String(quote.episode).padStart(2, '0')}`);
        if (quote.episode_title) parts.push(`· ${quote.episode_title}`);
        return parts.join(' ') || 'The Blacklist';
    };

    const handleCopy = async () => {
        try {
            const text = `"${quote.quote}" — Raymond Reddington`;
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    const handleShare = () => {
        const text = encodeURIComponent(
            `"${quote.quote}"\n\n— Raymond Reddington, The Blacklist`
        );
        window.open(
            `https://twitter.com/intent/tweet?text=${text}`,
            '_blank',
            'noopener,noreferrer'
        );
    };

    const handleSpeak = () => {
        if (speaking) {
            window.speechSynthesis.cancel();
            setSpeaking(false);
            return;
        }

        const utterance = new SpeechSynthesisUtterance(quote.quote);
        utterance.rate = 0.85;
        utterance.pitch = 0.85;
        utterance.volume = 1;

        const voices = window.speechSynthesis.getVoices();
        const preferredVoices = voices.filter(
            (v) =>
                v.name.toLowerCase().includes('male') ||
                v.name.toLowerCase().includes('david') ||
                v.name.toLowerCase().includes('daniel') ||
                v.name.toLowerCase().includes('james') ||
                v.name.toLowerCase().includes('mark') ||
                v.name.toLowerCase().includes('google uk english male')
        );
        if (preferredVoices.length > 0) {
            utterance.voice = preferredVoices[0];
        } else if (voices.length > 0) {
            const englishVoice = voices.find((v) => v.lang.startsWith('en'));
            if (englishVoice) utterance.voice = englishVoice;
        }

        utterance.onend = () => setSpeaking(false);
        utterance.onerror = () => setSpeaking(false);

        utteranceRef.current = utterance;
        setSpeaking(true);
        window.speechSynthesis.speak(utterance);
    };

    return (
        <div
            className={`quote-card ${rating >= 5 ? 'quote-card--iconic' : ''}`}
            style={{ animationDelay: `${index * 80}ms` }}
        >
            <div className="quote-card__meta-top">
                {character && character.toLowerCase() !== 'unknown' && (
                    <span className="quote-card__character">
                        <span className="quote-card__character-dot" />
                        To: {character}
                    </span>
                )}
                {rating > 0 && (
                    <span className="quote-card__stars" title={`Iconic rating: ${rating}/${MAX_STARS}`}>
                        {Array.from({ length: MAX_STARS }, (_, i) => (
                            <span key={i} className={`quote-card__star ${i < rating ? 'quote-card__star--filled' : ''}`}>
                                ★
                            </span>
                        ))}
                    </span>
                )}
            </div>

            <p className="quote-card__text">{quote.quote}</p>

            {quote.context && (
                <p className="quote-card__context">{quote.context}</p>
            )}

            <div className="quote-card__meta-bottom">
                {themes.length > 0 && (
                    <div className="quote-card__themes">
                        {themes.slice(0, 3).map((t) => (
                            <span key={t} className="quote-card__theme-badge">{t}</span>
                        ))}
                    </div>
                )}
                {quoteType && (
                    <span className={`quote-card__type-badge quote-card__type-badge--${quoteType}`}>
                        {quoteType}
                    </span>
                )}
            </div>

            <div className="quote-card__footer">
                <span className="quote-card__badge">🎬 {formatBadge()}</span>
                <div className="quote-card__actions">
                    <button
                        className={`quote-card__action-btn ${speaking ? 'speaking' : ''}`}
                        onClick={handleSpeak}
                        title={speaking ? 'Stop reading' : 'Read aloud'}
                    >
                        {speaking ? '⏹️' : '🔊'}
                    </button>
                    <button
                        className={`quote-card__action-btn ${copied ? 'copied' : ''}`}
                        onClick={handleCopy}
                        title="Copy quote"
                    >
                        {copied ? '✓' : '📋'}
                    </button>
                    <button
                        className="quote-card__action-btn"
                        onClick={handleShare}
                        title="Share on X"
                    >
                        𝕏
                    </button>
                </div>
            </div>
        </div>
    );
}
