# How to Start the Application

## Quick Start Commands

### Option 1: Production Mode (Flask serves React build)

**Step 1: Build React (already done ✅)**
```powershell
cd "D:\Cerevyn Solutions\TextToSpeech\frontend"
npm run build
```

**Step 2: Start Flask Server**
```powershell
cd "D:\Cerevyn Solutions\TextToSpeech"
python app.py
```

**Step 3: Open Browser**
Visit: `http://localhost:5000`

---

### Option 2: Development Mode (Separate servers)

**Terminal 1 - React Dev Server:**
```powershell
cd "D:\Cerevyn Solutions\TextToSpeech\frontend"
npm start
```
Runs on: `http://localhost:3000`

**Terminal 2 - Flask Backend:**
```powershell
cd "D:\Cerevyn Solutions\TextToSpeech"
python app.py
```
Runs on: `http://localhost:5000`

---

## Important Notes

- **Production Mode**: Flask serves the built React app from `frontend/build`
- **Development Mode**: React dev server runs separately with hot-reload
- Make sure Flask dependencies are installed: `pip install -r requirements.txt`
- Make sure React dependencies are installed: `npm install` (in frontend directory)

