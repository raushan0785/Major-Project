# 🚀 GenAI SRS Full Project Specification

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=flat&logo=google&logoColor=white)](https://ai.google.dev/)
[![Whisper AI](https://img.shields.io/badge/OpenAI%20Whisper-412991?style=flat&logo=openai&logoColor=white)](https://openai.com/research/whisper)

Welcome to the **GenAI SRS Project**, a comprehensive microservices-based application designed to automatically generate Software Requirements Specification (SRS) documents utilizing the power of LLMs (Google Gemini) and Audio Transcription (OpenAI Whisper).

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Architecture & Modules](#-architecture--modules)
- [Tech Stack](#-tech-stack)
- [Installation Strategy](#-installation-strategy)
  - [1. Backend API (ProjectBackend1)](#1-backend-api-projectbackend1)
  - [2. SRS Generation Service (srspipeline-main)](#2-srs-generation-service-srspipeline-main)
  - [3. Audio Transcription Service (whisper-main)](#3-audio-transcription-service-whisper-main)
  - [4. Frontend interface](#4-frontend-interface)
- [Environment Variables Overview](#-environment-variables-overview)
- [How to Run](#-how-to-run)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

Gathering project requirements, formatting them professionally into an IEEE or Agile template, and maintaining validation checks can be a tedious process. This project solves that by integrating **Google Gemini** for intelligent text generation and validation, alongside **OpenAI's Whisper** model to transcribe spoken requirements from audio files into text. 

Users can securely sign up, transcribe their voice recordings detailing their project, generate high-quality SRS documents across various templates, and download the outcomes—all tied together via a seamless API platform and frontend.

---

## 🏗 Architecture & Modules

The repository is modularized into four distinct domains:

1. **`ProjectBackend1/`**: The Core API Gateway & Identity Manager
   - Manages user authentication (Signup, Login, JWT tokens).
   - Handles the Database operations using MongoDB.
   - Orchestrates requests between the frontend and the AI microservices.
2. **`srspipeline-main/`**: The generative AI Pipeline
   - Interfaces heavily with the **Google Gemini API**.
   - Contains Logic for formatting outputs into templates like `Agile`, `IEEE`, `Minimal`, and `Startup`.
 
3. **`whisper-main/`**: Voice-to-Text inference 
   - Uses OpenAI's Whisper model to parse audio files.
   - Returns structured text reflecting the user's spoken software requirements.
4. **`frontend/`**: The Client Interface
   - A vanilla HTML/CSS/JS frontend styled with modern responsive components to interact intuitively with the core backend `/auth` and generative endpoints.

---

## 💻 Tech Stack

- **Frameworks**: FastAPI, Starlette
- **Database**: MongoDB (Motor Async Driver), SQLite for legacy data migrations.
- **AI/ML**: Google Gemini (via `google-generativeai`), OpenAI Whisper locally executed via PyTorch.
- **Security**: Passlib (Bcrypt), python-jose (JWT).
- **Frontend**: Vanilla Javascript (ES6), HTML5, CSS3.

---

## 🚀 Installation Strategy

To prevent dependency conflicts between different heavily-loaded ML packages (like `torch` combined with `google-generativeai`), it is highly recommended to set up individual virtual environments for each module.

Before starting, ensure you have:
- **Python 3.11+**
- **MongoDB** running locally (`mongodb://localhost:27017` by default).

### 1. Backend API (ProjectBackend1)
Acts as the main hub.

```bash
cd ProjectBackend1
python -m venv venv

# Activate venv (Windows)
.\venv\Scripts\Activate.ps1
# Activate venv (Mac/Linux)
# source venv/bin/activate

pip install -r requirements.txt
```

### 2. SRS Generation Service (srspipeline-main)
The LLM interaction microservice.

```bash
cd srspipeline-main
python -m venv venv
.\venv\Scripts\Activate.ps1

# Using uv (recommended)
uv sync
# OR using pip
pip install -e .
```

### 3. Audio Transcription Service (whisper-main)
The ML inference instance for voice.

```bash
cd whisper-main
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Frontend Interface
No installation required! Just serve the HTML statically.
```bash
cd frontend
# You can use a simple python server to view it
python -m http.server 3000
```
Open `http://localhost:3000` in your browser.

---

## 🔐 Environment Variables Overview

Create `.env` files in the root of the respective module folders:

**For `ProjectBackend1/.env`:**
```env
MONGODB_URL=mongodb://localhost:27017
DB_NAME=genai_srs
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**For `srspipeline-main/.env`:**
```env
GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🏃‍♂️ How to Run

Because this is a microservice architecture, you must run the services on distinct ports to avoid collision (e.g., `8000`, `8001`, `8002`).

**Terminal 1:** Run the Core Backend (Port 8000)
```bash
cd ProjectBackend1
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

**Terminal 2:** Run the SRS Pipeline (Port 8001)
*Ensure inside that module's `main.py`, the uvicorn hook is set to port 8001*
```bash
cd srspipeline-main
uv run python main.py
```

**Terminal 3:** Run the Whisper API (Port 8002)
*Ensure inside that module's `app.py`, the hook is set to port 8002*
```bash
cd whisper-main
python app.py
```

**Testing the APIs:**
Once running, you can visit the auto-generated Swagger UI docs for each respective service:
- ProjectBackend1: `http://localhost:8000/docs`
- SRSPipeline: `http://localhost:8001/docs` (Assuming port adjusted)
- Whisper: `http://localhost:8002/docs` (Assuming port adjusted)

---

## 🤝 Contributing

Contributions are always welcome! Whether it's expanding standard templates, improving the ML inference speed for whisper, or bug fixing.
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See individual modules for specific licensing details where applicable.
