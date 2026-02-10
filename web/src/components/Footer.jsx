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
                            📚 {stats.total_quotes} verified quotes · {stats.total_seasons} seasons · The Blacklist
                        </p>
                    )}
                    <a
                        href="http://localhost:8000/docs"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="footer__api-link"
                    >
                        ⚡ API Docs (Swagger)
                    </a>
                    <p className="footer__credit">
                        Built with ❤️ for fans of Raymond "Red" Reddington
                    </p>
                </div>
            </div>
        </footer>
    );
}
