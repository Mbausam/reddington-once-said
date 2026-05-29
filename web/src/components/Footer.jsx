import { useState, useEffect } from 'react';
import { getStats } from '../api';

export default function Footer() {
    const [stats, setStats] = useState(null);

    useEffect(() => {
        getStats()
            .then(setStats)
            .catch(console.error);
    }, []);

    return (
        <footer className="footer">
            <div className="container">
                <div className="footer__content">
                    <span className="footer__logo">Reddington Once Said</span>
                    {stats && (
                        <p className="footer__stats">
                            📚 {stats.total_quotes.toLocaleString()} quotes · {stats.total_seasons} seasons · {Object.keys(stats.themes || {}).length} themes · The Blacklist
                        </p>
                    )}
                    <div className="footer__links">
                        <a
                            href="/docs"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="footer__api-link"
                        >
                            ⚡ API Docs
                        </a>
                        <a
                            href="https://github.com/Mbausam/reddington-once-said"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="footer__api-link"
                        >
                            ☆ GitHub
                        </a>
                    </div>
                    <p className="footer__credit">
                        Built with passion for fans of Raymond "Red" Reddington
                    </p>
                </div>
            </div>
        </footer>
    );
}
