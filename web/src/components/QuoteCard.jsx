import { useState, useRef } from 'react';

export default function QuoteCard({ quote, index = 0 }) {
    const [copied, setCopied] = useState(false);
    const [speaking, setSpeaking] = useState(false);
    const utteranceRef = useRef(null);

    const formatBadge = () => {
        const parts = [];
        if (quote.season) parts.push(`S${quote.season}`);
        if (quote.episode) parts.push(`E${quote.episode}`);
        if (quote.episode_title) parts.push(`· ${quote.episode_title}`);
        return parts.join('') || 'The Blacklist';
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
            // Stop speaking
            window.speechSynthesis.cancel();
            setSpeaking(false);
            return;
        }

        const utterance = new SpeechSynthesisUtterance(quote.quote);
        utterance.rate = 0.85; // Slower, more deliberate like Red
        utterance.pitch = 0.85; // Slightly deeper
        utterance.volume = 1;

        // Try to find a deep male voice
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
            // Fallback: try to find any English voice
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
            className="quote-card"
            style={{ animationDelay: `${index * 80}ms` }}
        >
            <p className="quote-card__text">{quote.quote}</p>
            <div className="quote-card__footer">
                <span className="quote-card__badge">🎬 {formatBadge()}</span>
                <div className="quote-card__actions">
                    <button
                        className={`quote-card__action-btn ${speaking ? 'speaking' : ''}`}
                        onClick={handleSpeak}
                        title={speaking ? 'Stop reading' : 'Read aloud'}
                        id={`speak-btn-${index}`}
                    >
                        {speaking ? '⏹️' : '🔊'}
                    </button>
                    <button
                        className={`quote-card__action-btn ${copied ? 'copied' : ''}`}
                        onClick={handleCopy}
                        title="Copy quote"
                        id={`copy-btn-${index}`}
                    >
                        {copied ? '✓' : '📋'}
                    </button>
                    <button
                        className="quote-card__action-btn"
                        onClick={handleShare}
                        title="Share on X"
                        id={`share-btn-${index}`}
                    >
                        𝕏
                    </button>
                </div>
            </div>
        </div>
    );
}
