# Taylor Swift Lyrics Visualizer

This Streamlit app lets you enter the title of a Taylor Swift song, fetches the lyrics using the Genius API, and displays a word cloud based on the lyrics.

## Features
- Enter a Taylor Swift song title
- Fetch lyrics from Genius
- Display lyrics in a clean textbox
- Generate a visually appealing word cloud

## Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Sing-with-Streamlit
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Get a Genius API Access Token:**
   - Sign up at [Genius API](https://genius.com/developers)
   - Create an API client and copy your access token
   - You will be prompted to enter this token in the app (or set as an environment variable in future versions)

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## Deployment
You can deploy this app for free on [Streamlit Community Cloud](https://streamlit.io/cloud).

## License
MIT 