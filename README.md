# AURA - AI-powered Understanding of Regional Abuse

An explainable multilingual NLP platform for detecting hate speech, cyberbullying, caste-based abuse, and harmful narratives in Tamil, English, and Telugu social media content using code-mixed and Romanized Indian regional languages.

## Overview

**AURA** bridges the gap in content moderation for Indian regional languages written in Romanized (transliterated) form. It handles **Hinglish**, **Tanglish**, and **Tenglish** - languages that standard moderation tools struggle to process.

### Key Features

- **Linguistic Normalization**: Phonetic transliteration engine for Romanized regional languages
- **Multi-tier Classification**: Detects 9 categories of violations (casteism, religious hate, gender abuse, threats, cyberbullying, etc.)
- **Sarcasm Detection**: Identifies toxic sentiment disguised as polite language
- **Explainability**: Provides token-level highlighting and reasoning for flagged content
- **Analytics Dashboard**: Real-time moderation telemetry and geographical heatmaps

## Project Structure

```
Regional language/
├── backend/              # FastAPI backend service
│   ├── app/
│   │   ├── models.py     # Database models
│   │   ├── schemas.py    # Data validation schemas
│   │   ├── main.py       # Application initialization
│   │   ├── database.py   # Database configuration
│   │   ├── routers/      # API endpoints
│   │   └── services/     # Business logic
│   ├── requirements.txt  # Python dependencies
│   └── run.py           # Application entry point
├── frontend/             # React + Vite frontend
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── PROJECT_DOCUMENTATION.md
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- MySQL database

### Backend Setup

1. Navigate to backend directory:

```bash
cd backend
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file with configuration:

```env
DATABASE_URL=mysql+pymysql://user:password@localhost/dbname
SECRET_KEY=your_secret_key_here
```

5. Run the application:

```bash
python run.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Run development server:

```bash
npm run dev
```

4. Build for production:

```bash
npm run build
```

## API Endpoints

- `POST /api/analyze` - Analyze text for harmful content
- `POST /api/moderate` - Get moderation recommendations
- `GET /api/analytics` - Retrieve dashboard analytics
- `POST /api/report` - Submit user reports

## How It Works

1. **Input Processing**: User submits text via frontend or API
2. **Transliteration**: Phonetic engine normalizes Romanized regional language text
3. **Classification**: Multi-tier lexicon & semantic classifier processes normalized text
4. **Detection**: System identifies violations and checks for sarcasm/hidden toxicity
5. **Explainability**: Extracts exact phrases causing flags with token-level coordinates
6. **Output**: Returns color-coded highlights and reasoning to UI; logs to database

## Supported Languages

- Hindi (Hinglish)
- Tamil (Tanglish)
- Telugu (Tenglish)

## Safety & Compliance

This tool helps platforms comply with:

- IT Rules 2021 (India)
- Regional intermediary guidelines
- Content moderation standards for vernacular languages

## Business Impact

- Automates 90% of vernacular content screening
- Reduces moderation costs significantly
- Protects brand safety and platform reputation
- Ensures regulatory compliance

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

## Support

For questions or support, please reach out to the development team.

---

**Comprehensive documentation**: See [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) for detailed technical specifications, deployment guidelines, and optimization strategies.
