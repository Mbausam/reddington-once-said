import { useState, useEffect } from 'react';
import { getCharacters } from '../api';

export default function CharacterGallery({ onSelectCharacter }) {
    const [characters, setCharacters] = useState([]);
    const [activeCharacter, setActiveCharacter] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getCharacters()
            .then((data) => {
                setCharacters(data.characters || []);
                setLoading(false);
            })
            .catch((err) => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    const handleClick = (char) => {
        const next = activeCharacter === char.name ? null : char.name;
        setActiveCharacter(next);
        if (onSelectCharacter) onSelectCharacter(next);
    };

    if (loading) {
        return (
            <section className="character-gallery" id="characters">
                <div className="container">
                    <h2 className="section-title">Who Red Was Talking To</h2>
                    <div className="character-gallery__loading">
                        <span className="loading-dot" />
                        <span className="loading-dot" />
                        <span className="loading-dot" />
                    </div>
                </div>
            </section>
        );
    }

    if (characters.length === 0) return null;

    return (
        <section className="character-gallery" id="characters">
            <div className="container">
                <h2 className="section-title">Who Red Was Talking To</h2>
                <p className="section-subtitle">Every conversation has an audience. Find quotes by who was listening.</p>
                <div className="character-gallery__scroll">
                    {characters.map((char) => {
                        const isActive = activeCharacter === char.name;
                        return (
                            <button
                                key={char.name}
                                className={`character-gallery__card ${isActive ? 'character-gallery__card--active' : ''}`}
                                onClick={() => handleClick(char)}
                            >
                                <div className="character-gallery__avatar">
                                    <img
                                        src={char.image}
                                        alt={char.name}
                                        onError={(e) => {
                                            e.target.style.display = 'none';
                                            e.target.nextSibling.style.display = 'flex';
                                        }}
                                    />
                                    <span
                                        className="character-gallery__fallback"
                                        style={{ display: 'none' }}
                                    >
                                        {char.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
                                    </span>
                                </div>
                                <span className="character-gallery__name">{char.name}</span>
                                <span className="character-gallery__count">{char.quote_count} quotes</span>
                                {char.top_themes && char.top_themes.length > 0 && (
                                    <span className="character-gallery__themes">
                                        {char.top_themes.slice(0, 2).join(' · ')}
                                    </span>
                                )}
                            </button>
                        );
                    })}
                </div>
            </div>
        </section>
    );
}
