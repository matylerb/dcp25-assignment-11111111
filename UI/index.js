async function fetchTunes() {
    const response = await fetch('/api/tunes');
    const tunes = await response.json();
    return tunes;
  
}