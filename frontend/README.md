# CEREVAK Frontend

React frontend for the CEREVAK Multilingual Text-to-Speech Translator application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm start
```

The app will run on `http://localhost:3000` and proxy API requests to `http://localhost:5000`.

## Build for Production

To build the React app for production:

```bash
npm run build
```

This will create a `build` folder with the optimized production build. The Flask backend is configured to serve these static files.

## Environment Variables

Create a `.env` file in the frontend directory (optional):

```
REACT_APP_API_URL=http://localhost:5000
```

If not set, it defaults to `http://localhost:5000`.

## Features

- Cerevyn brand theme (navy background #051650, accent #2D2755)
- Clean card-based layout
- Input text or upload file
- Language selection
- Voice settings (gender, age tone)
- Speed control
- Audio playback and download

