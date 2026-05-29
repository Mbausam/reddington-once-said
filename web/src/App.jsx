import { useState } from 'react';
import './App.css'
import HeroSection from './components/HeroSection'
import StatsBanner from './components/StatsBanner'
import RandomQuote from './components/RandomQuote'
import ThemeCloud from './components/ThemeCloud'
import CharacterGallery from './components/CharacterGallery'
import IconicHall from './components/IconicHall'
import SearchBar from './components/SearchBar'
import SeasonExplorer from './components/SeasonExplorer'
import Footer from './components/Footer'

function App() {
  const [activeTheme, setActiveTheme] = useState(null);
  const [activeCharacter, setActiveCharacter] = useState(null);

  const scrollToRandom = () => {
    document.getElementById('random')?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToSearch = () => {
    document.getElementById('search')?.scrollIntoView({ behavior: 'smooth' });
  };

  // When a theme or character is selected, scroll to search with pre-filled filters
  const handleThemeSelect = (theme) => {
    setActiveTheme(theme);
    if (theme) scrollToSearch();
  };

  const handleCharacterSelect = (character) => {
    setActiveCharacter(character);
    if (character) scrollToSearch();
  };

  return (
    <>
      <HeroSection onScrollDown={scrollToRandom} />
      <StatsBanner />
      <ThemeCloud onSelectTheme={handleThemeSelect} />
      <RandomQuote />
      <CharacterGallery onSelectCharacter={handleCharacterSelect} />
      <IconicHall />
      <SearchBar />
      <SeasonExplorer />
      <Footer />
    </>
  );
}

export default App
