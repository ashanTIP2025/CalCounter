# 🍽️ Calorie Advisor

A Streamlit web app that analyzes food photos and provides calorie counts, macronutrient breakdown, and health tips using Google Gemini AI.

## Features

- Upload a food image (JPG, JPEG, PNG)
- AI-powered food identification and analysis
- Per-item breakdown: Calories, Protein, Carbs, Fat
- Total calorie count
- Personalized health tips

## Tech Stack

- [Streamlit](https://streamlit.io) — web app framework
- [Google Gemini AI](https://ai.google.dev) — image analysis
- [Pillow](https://python-pillow.org) — image handling
- [google-genai](https://pypi.org/project/google-genai/) — Google Gemini SDK
- [python-dotenv](https://pypi.org/project/python-dotenv/) — environment variable management

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ashanTIP2025/CalCounter.git
cd CalCounter
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your API key

Create a `.env` file in the root directory:

```
GOOGLE_API_KEY=your_google_api_key_here
```

Get your API key from [Google Cloud Console](https://console.cloud.google.com) with the Generative Language API enabled and billing linked.

### 4. Run the app

```bash
streamlit run app.py
```

## Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo and set `app.py` as the main file
4. Add your `GOOGLE_API_KEY` under **Advanced settings → Secrets**
5. Deploy
