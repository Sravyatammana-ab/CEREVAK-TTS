import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const translateAndSpeak = async ({ text, targetLang, voiceGender, pitch = 0, speed = 0 }) => {
  try {
    const response = await api.post('/api/translate-and-speak', {
      text,
      target_lang: targetLang,
      tts_engine: 'azure',
      voice_gender: voiceGender,
      rate: speed,
      pitch,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const getLanguages = async () => {
  try {
    const response = await api.get('/api/languages');
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export const getAudioUrl = (filename) => {
  return `${API_BASE_URL}/api/audio/${filename}`;
};

export const getDownloadUrl = (filename) => {
  return `${API_BASE_URL}/api/download/${filename}`;
};

export default api;

