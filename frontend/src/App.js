import React, { useState, useEffect } from 'react';
import './App.css';
import { translateAndSpeak, getLanguages, getAudioUrl, getDownloadUrl } from './api';

function App() {
  const [inputMethod, setInputMethod] = useState('type');
  const [inputText, setInputText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('te');
  const [voiceGender, setVoiceGender] = useState('Male');
  const [ageTone, setAgeTone] = useState('Adult');
  const [languages, setLanguages] = useState({});
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);

  useEffect(() => {
    loadLanguages();
  }, []);

  const loadLanguages = async () => {
    try {
      const langs = await getLanguages();
      setLanguages(langs);
      // Set default to Telugu if available
      if (langs['te']) {
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

    setLoading(true);
    setStatus(null);
    setResult(null);

    try {
      setStatus({ type: 'info', message: 'Detecting source language...' });
      
      const response = await translateAndSpeak(
        inputText,
        targetLanguage,
        voiceGender,
        ageTone
      );

      if (response.success) {
        setResult(response);
        setStatus({ type: 'success', message: 'Audio generated successfully!' });
      } else {
        setStatus({ type: 'error', message: response.error || 'Failed to generate audio' });
      }
    } catch (error) {
      setStatus({ 
        type: 'error', 
        message: error.error || error.message || 'An error occurred' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Header with Logo and Title */}
      <div className="header">
        <img src="/cerevyn_logo.png" alt="Cerevyn Logo" className="logo" />
        <h1 className="title">CEREVAK - Multilingual Text-to-Speech Translator</h1>
      </div>

      {/* Input Text Section */}
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
            {uploadedFile && (
              <div className="file-name">Selected: {uploadedFile.name}</div>
            )}
            {inputText && (
              <textarea
                className="text-area"
                value={inputText}
                readOnly
                rows="8"
                style={{ marginTop: '1rem' }}
              />
            )}
          </div>
        )}
      </div>

      {/* Target Language + Voice Settings */}
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

          <div className="setting-group">
            <label className="setting-label">Age Tone</label>
            <select
              className="select-box"
              value={ageTone}
              onChange={(e) => setAgeTone(e.target.value)}
            >
              <option value="Child">Child</option>
              <option value="Adult">Adult</option>
              <option value="Senior">Senior</option>
            </select>
          </div>
        </div>
      </div>

      {/* Generate Speech Button */}
      <div className="generate-button-container">
        <button
          className="generate-button"
          onClick={handleGenerate}
          disabled={loading || !inputText.trim()}
        >
          {loading ? (
            <>
              <span className="spinner" style={{ display: 'inline-block', marginRight: '0.5rem' }}></span>
              Generating...
            </>
          ) : (
            '🎵 Generate Speech'
          )}
        </button>
      </div>

      {/* Status Messages */}
      {status && (
        <div className={`status-message status-${status.type}`}>
          {status.type === 'info' && <span className="spinner"></span>}
          <span>{status.message}</span>
        </div>
      )}

      {/* Output Text + Audio Player + Download */}
      {result && (
        <div className="section-card">
          <h2 className="section-title">📊 Results</h2>
          
          <div className="output-grid">
            <div>
              <span className="output-label">Detected Language: {result.source_lang_name} ({result.source_lang})</span>
              <div className="output-text">{inputText}</div>
            </div>
            <div>
              <span className="output-label">Target Language: {result.target_lang_name} ({result.target_lang})</span>
              <div className="output-text">{result.translated_text}</div>
            </div>
          </div>

          <div className="audio-player-container" style={{ marginTop: '2rem' }}>
            <span className="output-label">Audio Output</span>
            {result.audio_url && result.filename && (
              <>
                <audio
                  className="audio-player"
                  controls
                  src={getAudioUrl(result.filename)}
                >
                  Your browser does not support the audio element.
                </audio>
                <a
                  href={getDownloadUrl(result.filename)}
                  download={result.filename}
                  className="download-button"
                >
                  📥 Download Audio (MP3)
                </a>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

