import React, { useEffect, useState } from 'react';
import { translateAndSpeak, getLanguages, getAudioUrl, getDownloadUrl } from '../api';
import '../App.css';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const [inputMethod, setInputMethod] = useState('type');
  const [inputText, setInputText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('te');
  const [voiceGender, setVoiceGender] = useState('Male');
  const ageTone = 'Adult';
  const [pitch, setPitch] = useState(0);
  const [languages, setLanguages] = useState({});
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [audioObjectUrl, setAudioObjectUrl] = useState(null);

  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    loadLanguages();
  }, []);

  useEffect(
    () => () => {
      if (audioObjectUrl) {
        URL.revokeObjectURL(audioObjectUrl);
      }
    },
    [audioObjectUrl]
  );

  const loadLanguages = async () => {
    try {
      const langs = await getLanguages();
      setLanguages(langs);
      if (langs.te) {
        setTargetLanguage('te');
      }
    } catch (error) {
      console.error('Error loading languages:', error);
      setStatus({ type: 'error', message: 'Failed to load languages' });
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setInputText(e.target.result);
      };
      reader.readAsText(file);
    }
  };

  const handleGenerate = async () => {
    if (!inputText.trim()) {
      setStatus({ type: 'error', message: 'Please enter some text' });
      return;
    }

    if (audioObjectUrl) {
      URL.revokeObjectURL(audioObjectUrl);
      setAudioObjectUrl(null);
    }

    setLoading(true);
    setStatus(null);
    setResult(null);

    try {
      setStatus({ type: 'info', message: 'Detecting source language...' });

      const response = await translateAndSpeak(
        inputText,
        targetLanguage,
        voiceGender,
        ageTone,
        'openai',
        null,
        pitch
      );

      if (response.success) {
        if (response.audio_base64 && response.filename) {
          const mimeType = response.filename.toLowerCase().endsWith('.wav') ? 'audio/wav' : 'audio/mpeg';
          const byteString = atob(response.audio_base64);
          const byteArray = new Uint8Array(byteString.length);
          for (let i = 0; i < byteString.length; i += 1) {
            byteArray[i] = byteString.charCodeAt(i);
          }
          const blob = new Blob([byteArray], { type: mimeType });
          const objectUrl = URL.createObjectURL(blob);
          setAudioObjectUrl(objectUrl);
        }
        setResult(response);
        setStatus({ type: 'success', message: 'Audio generated successfully!' });
      } else {
        setStatus({ type: 'error', message: response.error || 'Failed to generate audio' });
      }
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.error || error.message || 'An error occurred',
      });
    } finally {
      setLoading(false);
    }
  };

  const downloadLabel = result?.filename ? result.filename.split('.').pop().toUpperCase() : 'AUDIO';
  const pitchDisplay = pitch > 0 ? `+${pitch}` : `${pitch}`;

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="app">
      <header className="header">
        <div className="brand-row">
          <img src="/cerevyn_logo_text.png" alt="Cerevyn Solutions logo" className="brand-logo" />
          <h1 className="brand-name">Cerevak</h1>
        </div>
        <p className="tagline">Multilingual Text-to-Speech Translator</p>
        <div className="header-actions">
          {user && (
            <span className="welcome-badge">
              Welcome,&nbsp;
              <strong>{user.displayName}</strong>
            </span>
          )}
          <button className="header-button" type="button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      <div className="section-card">
        <h2 className="section-title">📝 Input Text</h2>
        <div className="section-subtitle">Choose input method:</div>
        <div className="input-method">
          <div className="radio-group">
            <div className="radio-option">
              <input
                type="radio"
                id="type-text"
                name="input-method"
                value="type"
                checked={inputMethod === 'type'}
                onChange={(e) => setInputMethod(e.target.value)}
              />
              <label htmlFor="type-text">Type Text</label>
            </div>
            <div className="radio-option">
              <input
                type="radio"
                id="upload-file"
                name="input-method"
                value="upload"
                checked={inputMethod === 'upload'}
                onChange={(e) => setInputMethod(e.target.value)}
              />
              <label htmlFor="upload-file">Upload Text File</label>
            </div>
          </div>
        </div>

        {inputMethod === 'type' ? (
          <textarea
            className="text-area"
            placeholder="Type or paste your text here in any language..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows="8"
          />
        ) : (
          <div className="file-upload">
            <input
              type="file"
              id="file-input"
              className="file-input"
              accept=".txt,.pdf,.doc,.docx"
              onChange={handleFileUpload}
            />
            <label htmlFor="file-input" className="file-label">
              Choose File (.txt, .pdf, .doc, .docx)
            </label>
            {uploadedFile && <div className="file-name">Selected: {uploadedFile.name}</div>}
            {inputText && (
              <textarea className="text-area" value={inputText} readOnly rows="8" style={{ marginTop: '1rem' }} />
            )}
          </div>
        )}
      </div>

      <div className="section-card">
        <div className="settings-grid">
          <div className="setting-group">
            <label className="setting-label">🎯 Target Language</label>
            <select
              className="select-box"
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
            >
              {Object.entries(languages).map(([code, name]) => (
                <option key={code} value={code}>
                  {name} ({code})
                </option>
              ))}
            </select>
          </div>

          <div className="setting-group">
            <label className="setting-label">🎤 Voice Gender</label>
            <div className="voice-radio-group">
              <div className="radio-option">
                <input
                  type="radio"
                  id="female"
                  name="voice-gender"
                  value="Female"
                  checked={voiceGender === 'Female'}
                  onChange={(e) => setVoiceGender(e.target.value)}
                />
                <label htmlFor="female">Female</label>
              </div>
              <div className="radio-option">
                <input
                  type="radio"
                  id="male"
                  name="voice-gender"
                  value="Male"
                  checked={voiceGender === 'Male'}
                  onChange={(e) => setVoiceGender(e.target.value)}
                />
                <label htmlFor="male">Male</label>
              </div>
            </div>
          </div>
        </div>

        <div className="pitch-control">
          <label className="pitch-label">
            Pitch Adjustment
            <span className="pitch-value">{pitchDisplay}</span>
            <span className="pitch-unit">semitones</span>
          </label>
          <input
            type="range"
            className="pitch-slider"
            min="-8"
            max="8"
            step="1"
            value={pitch}
            onChange={(e) => setPitch(parseInt(e.target.value, 10))}
            disabled={loading}
          />
          <div className="pitch-helper">
            Fine-tune the generated voice by shifting it up or down in 1-semitone steps.
          </div>
        </div>
      </div>

      <div className="generate-button-container">
        <button className="generate-button" onClick={handleGenerate} disabled={loading || !inputText.trim()}>
          {loading ? (
            <>
              <span className="spinner" style={{ display: 'inline-block', marginRight: '0.5rem' }} />
              Generating...
            </>
          ) : (
            '🎵 Generate Speech'
          )}
        </button>
      </div>

      {status && (
        <div className={`status-message status-${status.type}`}>
          {status.type === 'info' && <span className="spinner" />}
          <span>{status.message}</span>
        </div>
      )}

      {result && (
        <div className="section-card">
          <h2 className="section-title">📊 Results</h2>

          <div className="output-grid">
            <div>
              <span className="output-label">
                Detected Language: {result.source_lang_name} ({result.source_lang})
              </span>
              <div className="output-text">{inputText}</div>
            </div>
            <div>
              <span className="output-label">
                Target Language: {result.target_lang_name} ({result.target_lang})
              </span>
              <div className="output-text">{result.translated_text}</div>
            </div>
            {result.normalized_text && result.normalized_text !== result.translated_text && (
              <div>
                <span className="output-label">Normalized Text</span>
                <div className="output-text">{result.normalized_text}</div>
              </div>
            )}
          </div>

          <div className="audio-player-container" style={{ marginTop: '2rem' }}>
            <span className="output-label">Audio Output</span>
            {result.tts_engine && <div className="output-subtext">Engine: {result.tts_engine.toUpperCase()}</div>}
            {result.audio_url && result.filename && (
              <>
                <audio className="audio-player" controls src={audioObjectUrl || getAudioUrl(result.filename)}>
                  Your browser does not support the audio element.
                </audio>
                <a
                  href={audioObjectUrl || getDownloadUrl(result.filename)}
                  download={result.filename}
                  className="download-button"
                >
                  📥 Download Audio ({downloadLabel})
                </a>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;


