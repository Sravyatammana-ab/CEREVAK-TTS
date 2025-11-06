# OpenAI TTS Setup Guide

## Overview

This application now supports **OpenAI Text-to-Speech (TTS)** for high-quality voice generation with voice selection (male/female/neutral). The system automatically falls back to gTTS if OpenAI API key is not configured.

## What You Need

### ✅ OpenAI API Key

**Yes, you need an OpenAI API key** to use the high-quality TTS feature.

### How to Get OpenAI API Key

1. **Sign up for OpenAI Account**
   - Go to: https://platform.openai.com/
   - Create an account or sign in

2. **Get API Key**
   - Navigate to: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the API key (starts with `sk-...`)
   - ⚠️ **Important**: Save it immediately - you won't see it again!

3. **Add Credits** (if needed)
   - Go to: https://platform.openai.com/account/billing
   - Add payment method and credits
   - OpenAI TTS pricing: ~$15 per 1M characters

## Setup Instructions

### Option 1: Environment Variable (Recommended)

#### Windows (PowerShell)
```powershell
# Set for current session
$env:OPENAI_API_KEY="sk-your-api-key-here"

# Set permanently (User level)
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-api-key-here', 'User')
```

#### Windows (Command Prompt)
```cmd
# Set for current session
set OPENAI_API_KEY=sk-your-api-key-here

# Set permanently
setx OPENAI_API_KEY "sk-your-api-key-here"
```

#### Linux/Mac (Bash)
```bash
# Set for current session
export OPENAI_API_KEY="sk-your-api-key-here"

# Set permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export OPENAI_API_KEY="sk-your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Option 2: Create .env File (Alternative)

1. Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

2. Install python-dotenv:
   ```bash
   pip install python-dotenv
   ```

3. Update the code to load .env file (optional enhancement)

## Voice Selection Features

### Available Voices

**Female Voices:**
- **Nova** - Clear and expressive female voice
- **Shimmer** - Warm female voice

**Male Voices:**
- **Onyx** - Deep male voice
- **Echo** - Strong male voice

**Neutral Voices:**
- **Alloy** - Balanced neutral voice
- **Fable** - Versatile neutral voice

### How It Works

1. **Select Voice Type**: Choose Female, Male, or Neutral
2. **Select Specific Voice**: Pick from available voices in that category
3. **Generate Speech**: Click "Generate Speech" button
4. **System automatically uses OpenAI TTS** if API key is set
5. **Falls back to gTTS** if OpenAI is unavailable

## Cost Information

### OpenAI TTS Pricing

- **tts-1 model**: $15.00 per 1M characters
- **tts-1-hd model**: $30.00 per 1M characters (higher quality)

**Example Costs:**
- 1000 characters ≈ $0.015
- 10,000 characters ≈ $0.15
- 100,000 characters ≈ $1.50

### Free Alternative

- **gTTS (Google TTS)**: Free, unlimited
- Used automatically when OpenAI API key is not set
- Good quality but not as natural as OpenAI TTS

## Verification

After setting the API key, restart your Streamlit app:

```bash
streamlit run app/app.py
```

You should see:
- ✅ No "Tip" message about setting API key
- ✅ Voice selection available
- ✅ "OpenAI TTS" message when audio is generated

## Troubleshooting

### Issue: "OpenAI TTS failed, falling back to gTTS"

**Solutions:**
1. Verify API key is set: `echo $OPENAI_API_KEY` (Linux/Mac) or `echo %OPENAI_API_KEY%` (Windows)
2. Check API key is correct (starts with `sk-`)
3. Verify you have credits in your OpenAI account
4. Restart the application after setting the key
5. Check internet connection

### Issue: API Key Not Recognized

**Solutions:**
1. Restart terminal/command prompt after setting environment variable
2. Restart Streamlit application
3. Verify the key is set in the same terminal session where you run the app
4. Check for typos in the API key

### Issue: Rate Limits

**Solutions:**
1. Check your OpenAI account usage limits
2. Add more credits if needed
3. Wait a few minutes and try again

## Security Best Practices

1. **Never commit API keys to git**
   - Add `.env` to `.gitignore`
   - Don't share API keys publicly

2. **Use environment variables** instead of hardcoding

3. **Rotate API keys** periodically

4. **Monitor usage** in OpenAI dashboard

## Benefits of OpenAI TTS

✅ **Higher Quality**: More natural, human-like voices  
✅ **Voice Selection**: Choose from 6 different voices  
✅ **Better Pronunciation**: Especially for multilingual content  
✅ **Consistent Quality**: Reliable across all languages  
✅ **Professional Sound**: Suitable for production use  

## Fallback Behavior

If OpenAI API key is not set or fails:
- ✅ System automatically uses **gTTS** (free)
- ✅ No errors or interruptions
- ✅ Still generates audio successfully
- ✅ All features work normally

---

**Note**: The application works perfectly fine without OpenAI API key using gTTS. OpenAI TTS is an optional enhancement for higher quality.

