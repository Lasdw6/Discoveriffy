# 🎵 Discoverify

Discoverify is a Flask web application that analyzes your Spotify playlists and provides personalized music recommendations based on audio features. Connect your Spotify account, select a playlist, and get song recommendations that match the vibe of your music.

## Features

- 🔐 **Spotify OAuth Integration** - Secure login with your Spotify account
- 📊 **Playlist Analysis** - Analyzes audio features of your playlists (danceability, energy, valence, tempo, etc.)
- 🎯 **Smart Recommendations** - Get personalized song recommendations based on your playlist's audio characteristics
- 🎨 **Modern UI** - Clean and intuitive interface built with Bootstrap
- 🔄 **Token Management** - Automatic token refresh for seamless user experience

## Prerequisites

- Python 3.7 or higher
- A Spotify Developer Account
- pip (Python package manager)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Discoveriffy
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app details:
   - App name: Discoverify (or any name you prefer)
   - App description: Music discovery app
   - Redirect URI: `http://127.0.0.1:5000/callback`
5. After creating the app, you'll see your **Client ID** and **Client Secret**

### 5. Configure Environment Variables

1. Copy the example environment file:

   ```bash
   # On Windows (PowerShell)
   Copy-Item .env.example .env

   # On macOS/Linux
   cp .env.example .env
   ```

2. Open `.env` and fill in your credentials:

   ```env
   SECRET_KEY=your-random-secret-key-here
   CLIENT_ID=your-spotify-client-id
   CLIENT_SECRET=your-spotify-client-secret
   ```

   **Important Notes:**

   - Generate a secure random string for `SECRET_KEY`. You can use:
     ```python
     import secrets
     print(secrets.token_hex(24))
     ```
   - Never commit your `.env` file to version control (it's already in `.gitignore`)

### 6. Run the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

## Usage

1. **Start the App**: Run `python app.py` and navigate to `http://127.0.0.1:5000`
2. **Connect Spotify**: Click "Connect with Spotify" to authorize the application
3. **Select Playlist**: Browse your playlists and select one to analyze
4. **Get Recommendations**: View the playlist analysis and discover new songs that match your music taste!

## Project Structure

```
Discoveriffy/
├── app.py                 # Main Flask application
├── helpers.py             # Helper functions
├── main.py                # Example/test script
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore rules
├── static/
│   └── style.css          # Custom styles
└── templates/
    ├── base.html          # Base template
    ├── index.html         # Home page
    ├── login.html         # Login page
    ├── playlists.html     # Playlist selection
    ├── recommendations.html  # Recommendations display
    └── error.html         # Error page
```

## API Endpoints

- `GET /` - Home page
- `GET /login` - Initiate Spotify OAuth flow
- `GET /callback` - OAuth callback handler
- `GET /playlists` - Display user's playlists
- `GET /analyze/<playlist_id>` - Analyze playlist and show recommendations
- `GET /logout` - Log out user

## Technologies Used

- **Flask** - Web framework
- **Spotify Web API** - Music data and recommendations
- **Bootstrap** - UI framework
- **python-dotenv** - Environment variable management
- **requests** - HTTP library for API calls

## Security Notes

- All sensitive credentials are stored in environment variables
- Flask session management with secure secret keys
- OAuth 2.0 flow for secure Spotify authentication
- Never commit `.env` files or sensitive data

## Troubleshooting

### "Invalid client" error

- Verify your `CLIENT_ID` and `CLIENT_SECRET` in `.env` are correct
- Ensure your redirect URI in Spotify Dashboard matches `http://127.0.0.1:5000/callback`

### "Token expired" error

- The app should automatically refresh tokens, but if issues persist, try logging out and back in

### No recommendations found

- Try with a playlist that has more tracks
- Ensure the playlist has valid tracks with audio features available

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available for public use.

## Acknowledgments

- Spotify Web API for providing music data
- Flask community for the excellent framework
