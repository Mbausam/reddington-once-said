import './App.css'
import HeroSection from './components/HeroSection'
import RandomQuote from './components/RandomQuote'
import SearchBar from './components/SearchBar'
import SeasonExplorer from './components/SeasonExplorer'
import Footer from './components/Footer'

function App() {
  const scrollToRandom = () => {
    document.getElementById('random')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <>
      <HeroSection onScrollDown={scrollToRandom} />
      <RandomQuote />
      <SearchBar />
      <SeasonExplorer />
      <Footer />
    </>
  );
}

export default App
