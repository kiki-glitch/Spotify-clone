# 🎧 Spotify Clone (Music Explorer)

This Django-based Spotify clone app allows users to:
- Explore top artists and tracks from Spotify
- View detailed track info including album cover, artist, duration
- Stream audio previews (via 3rd-party API)
- Register, login, and access protected content
- Scrape track images from the Spotify track page

---

## 🚀 Features

- 🔐 User authentication (Signup, Login, Logout)
- 🎵 Explore weekly top artists
- 📈 Browse top trending tracks
- 🧠 Intelligent track metadata fetch via RapidAPI
- 🔊 Audio preview with duration (via YouTube audio fallback)
- 🖼️ Album art scraping from Spotify using BeautifulSoup
- 🎯 Role-protected access using Django's login_required

---

## 🛠️ Tech Stack

| Tool            | Description                          |
|-----------------|--------------------------------------|
| Django          | Backend framework                    |
| HTML/CSS        | Templates for rendering views        |
| BeautifulSoup   | For scraping Spotify track images    |
| RapidAPI        | Spotify Scraper API (3rd-party)      |
| Django Messages | For frontend user feedback           |
| Python `requests` | API calls and data fetching        |

---

## 📚 API Endpoints & Views

| Endpoint       | Description                                   |
|----------------|-----------------------------------------------|
| `/`            | Home – Displays top weekly artists            |
| `/login`       | User login page                               |
| `/signup`      | User registration                             |
| `/logout`      | Logout and redirect to login                  |
| `/music/<id>`  | Track details: image, audio, duration         |

---

## 📦 Functions Overview

### 🔝 `top_artists()`
- Fetches top weekly artists from the Spotify Scraper API
- Removes duplicate artist entries
- Returns a list of `(name, avatar_url, artist_id)`

### 🔊 `top_tracks()`
- Fetches top tracks
- Returns a trimmed list of top 18 tracks with:
  - Track ID
  - Name
  - Artist
  - Cover image URL

### 🎧 `get_audio_details(query)`
- Fetches audio preview info (URL + duration)
- Returns audio URL and duration (from YouTube via API)

### 🖼️ `get_track_image(track_id, track_name)`
- Scrapes Spotify web page for album cover (`640w` size)

---

## 🔐 Authentication System

- Uses Django's built-in `User` model and `auth` module
- Signup with email, username, and password confirmation
- Redirects after login
- Error handling with Django messages

---

## 🧪 Error Handling & Logging

- API and scraping wrapped in `try/except`
- Handles:
  - Network errors
  - Missing keys or malformed data
  - Empty audio or image results

---

## 🚫 Limitations (Free Tier Notice)

⚠️ Some RapidAPI endpoints require a paid plan.  
This app avoids premium endpoints and gracefully handles failures.

---

## 📸 Screenshots (Optional)

- Home page with top artists
- Music page with album art and audio preview
- Login/signup UI

---

## ⚙️ Setup Instructions

```bash
# 1. Clone the repo
git clone https://github.com/your-username/spotify-clone.git
cd spotify-clone

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your RapidAPI key in settings.py or .env
RAPID_API_KEY = "your-api-key-here"

# 5. Run the server
python manage.py runserver
