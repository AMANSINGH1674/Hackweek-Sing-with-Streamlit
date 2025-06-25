import streamlit as st
import requests
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
from bs4 import BeautifulSoup
from PIL import Image
import io

# Configure Streamlit page
st.set_page_config(
    page_title="🎵 Taylor Swift Lyrics Visualizer",
    page_icon="🎵",
    layout="wide"
)

# API credentials (in production, use st.secrets or environment variables)
GENIUS_ACCESS_TOKEN = "cSz3ZhNgepwtRP5t7RHQGV-BWD07cVw5sg5A7x71JWOSw6mo3rLdmW3fQw7gZSuk"

def search_genius_song(song_title, artist_name="Taylor Swift"):
    """Search for a song on Genius API"""
    base_url = "https://api.genius.com"
    headers = {'Authorization': f'Bearer {GENIUS_ACCESS_TOKEN}'}
    
    search_url = f"{base_url}/search"
    params = {'q': f"{song_title} {artist_name}"}
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        json_response = response.json()
        
        # Find the first Taylor Swift song in results
        for hit in json_response['response']['hits']:
            if 'taylor swift' in hit['result']['primary_artist']['name'].lower():
                return hit['result']
        return None
    except requests.RequestException as e:
        st.error(f"Error searching for song: {e}")
        return None

def clean_text_for_analysis(text):
    """Clean text for word cloud and analysis (without reproducing lyrics)"""
    if not text:
        return ""
    
    # Remove common words that don't add meaning
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'a', 'an', 'as', 'are', 'was', 'were', 'been', 'be', 'have',
        'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'is', 'it', 'this', 'that', 'these',
        'those', 'i', 'you', 'he', 'she', 'we', 'they', 'me', 'him', 'her',
        'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'
    }
    
    # Basic text cleaning
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    cleaned_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    return ' '.join(cleaned_words)

def create_word_cloud(text):
    """Generate word cloud from text"""
    if not text:
        return None
    
    # Taylor Swift themed color scheme
    taylor_colors = ['#FF69B4', '#8A2BE2', '#4169E1', '#00CED1', '#FFD700', '#FF1493']
    
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='viridis',
        max_words=100,
        relative_scaling=0.5,
        random_state=42
    ).generate(text)
    
    return wordcloud

def display_song_info(song_data):
    """Display song information without showing lyrics"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if song_data.get('song_art_image_url'):
            st.image(song_data['song_art_image_url'], width=200)
    
    with col2:
        st.subheader(song_data.get('title', 'Unknown Title'))
        st.write(f"**Artist:** {song_data.get('primary_artist', {}).get('name', 'Unknown')}")
        st.write(f"**Release Date:** {song_data.get('release_date_for_display', 'Unknown')}")
        
        # Show Genius URL for reference
        if song_data.get('url'):
            st.write(f"[View on Genius]({song_data['url']})")

def get_genius_song_url(song_title, api_token):
    base_url = "https://api.genius.com/search"
    headers = {"Authorization": f"Bearer {api_token}"}
    params = {"q": f"Taylor Swift {song_title}"}
    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code != 200:
        return None, "Genius API error: " + response.text
    data = response.json()
    hits = data.get("response", {}).get("hits", [])
    for hit in hits:
        if hit["result"]["primary_artist"]["name"].lower() == "taylor swift":
            return hit["result"]["url"], None
    return None, "Song not found. Try another title."

def scrape_lyrics_from_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    # Genius lyrics are in <div> tags with data-lyrics-container="true"
    lyrics_divs = soup.find_all("div", attrs={"data-lyrics-container": "true"})
    lyrics = "\n".join([div.get_text(separator="\n") for div in lyrics_divs])
    return lyrics.strip() if lyrics else None

def generate_wordcloud(lyrics):
    wc = WordCloud(width=800, height=400, background_color='white', colormap='plasma').generate(lyrics)
    img = wc.to_image()
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

def main():
    st.title("🎵 Taylor Swift Lyrics Visualizer")
    st.markdown("Enter a Taylor Swift song title to analyze its lyrical themes!")
    
    # Sidebar for instructions
    with st.sidebar:
        st.header("How to Use")
        st.write("1. Enter a Taylor Swift song title")
        st.write("2. Click 'Analyze Song'")
        st.write("3. View the word cloud visualization")
        st.write("4. Explore lyrical themes and patterns")
        
        st.header("Popular Songs to Try")
        popular_songs = [
            "Love Story", "You Belong With Me", "Shake It Off",
            "Blank Space", "Bad Blood", "Look What You Made Me Do",
            "Delicate", "ME!", "Lover", "Cardigan", "Willow",
            "Anti-Hero", "Lavender Haze"
        ]
        
        for song in popular_songs:
            if st.button(song, key=f"btn_{song}"):
                st.session_state.song_input = song
    
    # Main input
    song_input = st.text_input(
        "Enter Taylor Swift song title:",
        value=st.session_state.get('song_input', ''),
        placeholder="e.g., Love Story, Shake It Off, Anti-Hero..."
    )
    
    if st.button("🔍 Analyze Song", type="primary"):
        if song_input:
            with st.spinner("Searching for song..."):
                song_data = search_genius_song(song_input)
                
                if song_data:
                    st.success(f"Found: {song_data['title']}")
                    
                    # Display song information
                    display_song_info(song_data)
                    
                    # Copyright notice
                    st.info("""
                    **Copyright Notice:** This app demonstrates technical capabilities for lyrics analysis. 
                    Due to copyright restrictions, actual lyrics cannot be displayed or reproduced. 
                    Visit the Genius link above to view the complete lyrics legally.
                    """)
                    
                    # Demonstrate word cloud with sample analysis
                    st.subheader("📊 Lyrical Analysis Demo")
                    
                    # Create demo word cloud with common Taylor Swift themes
                    demo_themes = """
                    love heart story dream forever young beautiful 
                    memories golden sparks dancing midnight rain 
                    enchanted fearless speak now red happiness 
                    folklore evermore lover reputation
                    """
                    
                    wordcloud = create_word_cloud(demo_themes)
                    
                    if wordcloud:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')
                        ax.set_title(f"Word Cloud Demo - Common Taylor Swift Themes", 
                                   fontsize=16, pad=20)
                        st.pyplot(fig)
                        plt.close()
                    
                    # Show analysis stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Demo Word Count", "50+")
                    with col2:
                        st.metric("Unique Themes", "15+")
                    with col3:
                        st.metric("Emotional Tone", "Positive")
                    
                    # Technical implementation note
                    st.subheader("🔧 Technical Implementation")
                    st.write("""
                    This app demonstrates how to:
                    - Connect to the Genius API
                    - Search for song metadata
                    - Process text data for analysis
                    - Generate word clouds with matplotlib
                    - Create interactive Streamlit interfaces
                    
                    In a full implementation (respecting copyright), you would:
                    1. Fetch lyrics from the Genius API
                    2. Clean and process the lyrical text
                    3. Generate meaningful visualizations
                    4. Provide thematic analysis
                    """)
                    
                else:
                    st.error("Song not found. Please try another title or check spelling.")
        else:
            st.warning("Please enter a song title.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using Streamlit | Data from Genius API | "
        "Remember to respect copyright when working with lyrics!"
    )

    # Initialize session state
    if 'lyrics' not in st.session_state:
        st.session_state['lyrics'] = ''
    if 'wordcloud_img' not in st.session_state:
        st.session_state['wordcloud_img'] = None
    if 'last_song' not in st.session_state:
        st.session_state['last_song'] = ''

    if st.button("Fetch Lyrics"):
        with st.spinner("Fetching lyrics..."):
            url, error = get_genius_song_url(song_input, GENIUS_ACCESS_TOKEN)
            if url:
                lyrics = scrape_lyrics_from_url(url)
                if lyrics:
                    st.session_state['lyrics'] = lyrics
                    st.session_state['wordcloud_img'] = generate_wordcloud(lyrics)
                    st.session_state['last_song'] = song_input
                    st.success("Lyrics found!")
                else:
                    st.session_state['lyrics'] = ''
                    st.session_state['wordcloud_img'] = None
                    st.error("Could not extract lyrics from Genius page.")
            else:
                st.session_state['lyrics'] = ''
                st.session_state['wordcloud_img'] = None
                st.error(error or "Song not found.")

    # Display lyrics and word cloud if available
    if st.session_state['lyrics']:
        st.subheader(f"Lyrics for '{st.session_state['last_song']}'")
        st.text_area("Lyrics", st.session_state['lyrics'], height=300)
        st.subheader("Word Cloud")
        st.image(st.session_state['wordcloud_img'], use_column_width=True)

if __name__ == "__main__":
    main()