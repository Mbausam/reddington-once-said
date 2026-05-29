import { useState, useEffect } from 'react';
import { getThemes, getFilteredQuotes } from '../api';

export default function ThemeCloud({ onSelectTheme }) {
    const [themes, setThemes] = useState({});
    const [activeTheme, setActiveTheme] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getThemes()
            .then((data) => {
                setThemes(data.themes || {});
                setLoading(false);
            })
            .catch((err) => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    const handleClick = (theme) => {
        const next = activeTheme === theme ? null : theme;
        setActiveTheme(next);
        if (onSelectTheme) onSelectTheme(next);
    };

    if (loading) {
        return (
            <section className="theme-cloud" id="themes">
                <div className="container">
                    <h2 className="section-title">Explore by Theme</h2>
                    <div className="theme-cloud__loading">
                        <span className="loading-dot" />
                        <span className="loading-dot" />
                        <span className="loading-dot" />
                    </div>
                </div>
            </section>
        );
    }

    const entries = Object.entries(themes);
    if (entries.length === 0) return null;

    const maxCount = Math.max(...entries.map(([, c]) => c));

    return (
        <section className="theme-cloud" id="themes">
            <div className="container">
                <h2 className="section-title">Explore by Theme</h2>
                <p className="section-subtitle">Every lesson Red ever taught, organized by what matters</p>
                <div className="theme-cloud__grid">
                    {entries.map(([theme, count]) => {
                        const intensity = count / maxCount;
                        const isActive = activeTheme === theme;
                        return (
                            <button
                                key={theme}
                                className={`theme-cloud__chip ${isActive ? 'theme-cloud__chip--active' : ''}`}
                                style={{
                                    '--intensity': intensity,
                                    fontSize: `${0.8 + intensity * 0.4}rem`,
                                }}
                                onClick={() => handleClick(theme)}
                                title={`${count} quotes about ${theme}`}
                            >
                                <span className="theme-cloud__chip-name">{theme}</span>
                                <span className="theme-cloud__chip-count">{count}</span>
                            </button>
                        );
                    })}
                </div>
                {activeTheme && (
                    <p className="theme-cloud__active-label">
                        Showing quotes about <strong>{activeTheme}</strong>
                        <button className="theme-cloud__clear" onClick={() => handleClick(activeTheme)}>✕ Clear</button>
                    </p>
                )}
            </div>
        </section>
    );
}
