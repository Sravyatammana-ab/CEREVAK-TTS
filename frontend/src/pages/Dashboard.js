import React, { useEffect, useState } from 'react';
import { translateAndSpeak, getLanguages, getAudioUrl, getDownloadUrl } from '../api';
import '../App.css';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const [inputMethod, setInputMethod] = useState('type');
  const [inputText, setInputText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('');
  const [pitch, setPitch] = useState(0);
  const [speed, setSpeed] = useState(0);
  const [voiceGender, setVoiceGender] = useState('Female');
  const [languages, setLanguages] = useState({});
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [audioObjectUrl, setAudioObjectUrl] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);

  const { displayName, logout } = useAuth();
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

  useEffect(() => {
    if (!targetLanguage) {
      return;
    }
    const language = languages[targetLanguage];
    if (!language) {
      return;
    }
    const genders = language.available_genders || [];
    if (genders.length === 0) {
      return;
    }
    const normalizedCurrent = voiceGender.toLowerCase();
    if (!genders.map((g) => g.toLowerCase()).includes(normalizedCurrent)) {
      if (genders.includes('female')) {
        setVoiceGender('Female');
      } else if (genders.includes('male')) {
        setVoiceGender('Male');
      } else {
        const fallback = genders[0];
        setVoiceGender(fallback.charAt(0).toUpperCase() + fallback.slice(1));
      }
    }
  }, [targetLanguage, languages, voiceGender]);

  const loadLanguages = async () => {
    try {
      const langs = await getLanguages();
      setLanguages(langs);
      const defaultCode = langs.en ? 'en' : Object.keys(langs)[0];
      if (defaultCode) {
        setTargetLanguage(defaultCode);
        const genders = langs[defaultCode]?.available_genders || [];
        if (genders.includes('female')) {
          setVoiceGender('Female');
        } else if (genders.includes('male')) {
          setVoiceGender('Male');
        } else if (genders.length > 0) {
          setVoiceGender(genders[0].charAt(0).toUpperCase() + genders[0].slice(1));
        }
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

    if (!targetLanguage) {
      setStatus({ type: 'error', message: 'Please select a target language' });
      return;
    }

    if (audioObjectUrl) {
      URL.revokeObjectURL(audioObjectUrl);
      setAudioObjectUrl(null);
    }
    setAudioBlob(null);

    setLoading(true);
    setStatus(null);
    setResult(null);

    try {
      setStatus({ type: 'info', message: 'Detecting source language...' });

      const response = await translateAndSpeak({
        text: inputText,
        targetLang: targetLanguage,
        voiceGender,
        pitch,
        speed,
      });

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
          setAudioBlob(blob);
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
  const speedDisplay = speed > 0 ? `+${speed}%` : `${speed}%`;
  const selectedLanguageDetails = targetLanguage ? languages[targetLanguage] : null;
  const availableGenders = selectedLanguageDetails?.available_genders || [];

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout failed', error);
      setStatus({ type: 'error', message: 'Unable to log out. Please try again.' });
    }
  };

  const handleDownload = async () => {
    try {
      let blob = audioBlob;

      if (!blob && result?.filename) {
        const response = await fetch(getDownloadUrl(result.filename));
        if (!response.ok) {
          throw new Error(`Download failed with status ${response.status}`);
        }
        blob = await response.blob();
      }

      if (!blob) {
        setStatus({ type: 'error', message: 'No audio available to download yet.' });
        return;
      }

      const downloadUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = result?.filename || 'speech.mp3';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Download failed', error);
      setStatus({ type: 'error', message: 'Download failed. Please try again.' });
    }
  };

  return (
    <div className="app dashboard">
      <header className="dashboard-banner">
        <div className="dashboard-banner__content">
          <img
            src="/Cerevyn_logo_with_text-removebg-preview.png"
            alt="Cerevyn Solutions logo"
            className="dashboard-banner__logo"
          />
          <div className="dashboard-banner__text">
            <h1 className="dashboard-banner__title">CEREVAK</h1>
            <p className="dashboard-banner__subtitle">MULTILINGUAL TEXT-TO-SPEECH TRANSLATOR</p>
          </div>
        </div>
        <div className="dashboard-banner__meta">
          {displayName && <span className="dashboard-banner__welcome">Welcome, {displayName}</span>}
          <button className="dashboard-banner__logout" type="button" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      <div className="panel">
        <h2 className="panel__title">Input Text</h2>
        <div className="panel__subtitle">Choose input method:</div>
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

      <div className="panel panel--grid">
        <div className="panel__column">
          <label className="setting-label">Target Language</label>
          <select
            className="select-box"
            value={targetLanguage}
            onChange={(e) => setTargetLanguage(e.target.value)}
          >
            {Object.keys(languages).map((code) => {
              const language = languages[code];
              if (!language) {
                return null;
              }
              return (
                <option key={code} value={code}>
                  {language.name} ({code})
                </option>
              );
            })}
          </select>
        </div>

        <div className="panel__column">
          <label className="setting-label">Voice Selection</label>
          <div className="voice-radio-group">
            <label className="voice-radio-option">
              <input
                type="radio"
                name="voice-gender"
                value="Female"
                checked={voiceGender === 'Female'}
                onChange={(e) => setVoiceGender(e.target.value)}
                disabled={!availableGenders.includes('female') || loading}
              />
              <span>Female</span>
            </label>
            <label className="voice-radio-option">
              <input
                type="radio"
                name="voice-gender"
                value="Male"
                checked={voiceGender === 'Male'}
                onChange={(e) => setVoiceGender(e.target.value)}
                disabled={!availableGenders.includes('male') || loading}
              />
              <span>Male</span>
            </label>
            {!availableGenders.includes('male') && !availableGenders.includes('female') && (
              <span className="voice-placeholder">Voice options unavailable for this language.</span>
            )}
          </div>
        </div>

        <div className="panel__column">
          <div className="control-block">
            <label className="control-label">
              Pitch
              <span className="control-value">{pitchDisplay}</span>
            </label>
            <input
              type="range"
              className="control-slider"
              min="-3"
              max="3"
              step="1"
              value={pitch}
              onChange={(e) => setPitch(parseInt(e.target.value, 10))}
              disabled={loading}
            />
            <div className="control-helper">Lower values deepen the voice, higher values brighten it.</div>
          </div>
        </div>

        <div className="panel__column">
          <div className="control-block">
            <label className="control-label">
              Speed
              <span className="control-value">{speedDisplay}</span>
            </label>
            <input
              type="range"
              className="control-slider"
              min="-50"
              max="50"
              step="5"
              value={speed}
              onChange={(e) => setSpeed(parseInt(e.target.value, 10))}
              disabled={loading}
            />
            <div className="control-helper">Fine-tune speaking rate in percentages relative to the base voice.</div>
          </div>
        </div>
      </div>

      <div className="generate-button-container">
        <button
          className="generate-button"
          onClick={handleGenerate}
          disabled={loading || !inputText.trim() || !targetLanguage}
        >
          {loading ? (
            <>
              <span className="spinner" style={{ display: 'inline-block', marginRight: '0.5rem' }} />
              Generating...
            </>
          ) : (
            'Generate Speech'
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
        <div className="panel">
          <h2 className="panel__title">Output</h2>

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
            {result.audio_url && result.filename && (
              <>
                <audio className="audio-player" controls src={audioObjectUrl || getAudioUrl(result.filename)}>
                  Your browser does not support the audio element.
                </audio>
                <button type="button" className="download-button" onClick={handleDownload}>
                  Download Audio ({downloadLabel})
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;


