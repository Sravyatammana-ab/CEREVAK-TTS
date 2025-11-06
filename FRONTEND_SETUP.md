# Frontend Setup Guide

This project now uses a React frontend with the Cerevyn brand theme. Follow these steps to set it up:

## Prerequisites

- Node.js (v14 or higher) and npm installed
- Python 3.7+ with all backend dependencies installed

## Setup Steps

### 1. Install Frontend Dependencies

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

### 2. Development Mode

For development, you can run the React app separately:

```bash
# In frontend directory
npm start
```

This will start the React dev server on `http://localhost:3000` and proxy API requests to the Flask backend at `http://localhost:5000`.

**Note:** Make sure the Flask backend is running on port 5000.

### 3. Production Build

To build the React app for production:

```bash
# In frontend directory
npm run build
```

This creates a `build` folder with optimized static files.

### 4. Run Flask Backend (Serves React Build)

After building, the Flask backend will serve the React app:

```bash
# In project root
python app.py
```

The app will be available at `http://localhost:5000`.

## Project Structure

```
TextToSpeech/
├── frontend/              # React frontend
│   ├── public/           # Static assets
│   ├── src/              # React source code
│   └── package.json      # Frontend dependencies
├── app.py                # Flask backend (serves React build)
├── services/             # Backend services
└── output/              # Generated audio files
```

## Features

- **Cerevyn Brand Theme**: Navy background (#051650) with accent color (#2D2755)
- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Card-based layout with glow effects
- **Full Functionality**: All features from Streamlit version

## Troubleshooting

### Port Already in Use

If port 3000 is in use, React will ask to use a different port. You can also set it manually:

```bash
PORT=3001 npm start
```

### CORS Issues

The Flask backend has CORS enabled. If you encounter CORS errors, make sure:
1. Flask backend is running
2. `flask-cors` is installed: `pip install flask-cors`

### Build Not Found

If Flask can't find the React build:
1. Make sure you ran `npm run build` in the frontend directory
2. Check that `frontend/build` folder exists
3. Verify Flask is looking in the correct path (check `app.py`)

