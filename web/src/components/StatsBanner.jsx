import { useState, useEffect, useRef } from 'react';
import { getStats } from '../api';

export default function StatsBanner() {
    const [stats, setStats] = useState(null);
    const [visible, setVisible] = useState(false);
    const ref = useRef(null);

    useEffect(() => {
        getStats().then(setStats).catch(console.error);
    }, []);

    useEffect(() => {
        const el = ref.current;
        if (!el) return;
        const observer = new IntersectionObserver(
            ([entry]) => { if (entry.isIntersecting) setVisible(true); },
            { threshold: 0.3 }
        );
        observer.observe(el);
        return () => observer.disconnect();
    }, []);

    if (!stats) return null;

    const statItems = [
        { value: stats.total_quotes, label: 'Quotes', icon: '💬' },
        { value: stats.total_seasons, label: 'Seasons', icon: '📺' },
        { value: Object.keys(stats.themes || {}).length, label: 'Themes', icon: '🏷️' },
        { value: Object.keys(stats.characters || {}).length, label: 'Characters', icon: '👤' },
    ];

    return (
        <section className="stats-banner" ref={ref}>
            <div className="container">
                <div className="stats-banner__grid">
                    {statItems.map((item) => (
                        <div key={item.label} className="stats-banner__item">
                            <span className="stats-banner__icon">{item.icon}</span>
                            <span className={`stats-banner__value ${visible ? 'stats-banner__value--animated' : ''}`}>
                                {visible ? <CountUp target={item.value} /> : '0'}
                            </span>
                            <span className="stats-banner__label">{item.label}</span>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}

function CountUp({ target, duration = 1500 }) {
    const [count, setCount] = useState(0);

    useEffect(() => {
        if (target === 0) return;
        let start = 0;
        const increment = target / (duration / 16);
        const timer = setInterval(() => {
            start += increment;
            if (start >= target) {
                setCount(target);
                clearInterval(timer);
            } else {
                setCount(Math.floor(start));
            }
        }, 16);
        return () => clearInterval(timer);
    }, [target, duration]);

    return <>{count.toLocaleString()}</>;
}
