# POPclub Copilot v2

An enterprise-grade Retrieval-Augmented Generation (RAG) platform that couples an optimized, asynchronous **FastAPI** backend with a high-contrast minimalist **Next.js** client interface. This system uses **ChromaDB** for persistent vector storage and **Gemini 2.5 Flash** to provide reliable, context-grounded factual answers based on verified corporate documentation, preventing hallucinations entirely.

![Language](https://img.shields.io/badge/language-TypeScript%20%7C%20Python-blue)
![Framework](https://img.shields.io/badge/framework-FastAPI%20%7C%20Next.js-emerald)
![AI](https://img.shields.io/badge/AI-Google%20Gemini%202.5-red)
![Database](https://img.shields.io/badge/VectorDB-ChromaDB-orange)

---

## Table of Contents

1. [Key Architecture Upgrades (v1 vs v2)](#key-architecture-upgrades-v1-vs-v2)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Installation & Local Setup](#installation--local-setup)
6. [Usage & Knowledge Base Ingestion](#usage--knowledge-base-ingestion)
7. [API Reference](#api-reference)

---

## Key Architecture Upgrades (v1 vs v2)

- **From Unstructured to RAG:** Version 1 loaded a static JSON file directly into memory. Version 2 introduces an industry-standard semantic search pipeline using **ChromaDB** vector storage and `all-MiniLM-L6-v2` text embeddings to query large-scale documentation fragments dynamically.
- **From Express to FastAPI:** Rewritten in asynchronous **Python/FastAPI** with strict **Pydantic** data schema enforcement to achieve enterprise-grade fail-fast routing validations.
- **From Vanilla JS to Next.js + TS:** The client has been completely re-engineered around the modern **Next.js App Router** and **TypeScript** for compile-time safety and a polished, minimalist user interface layout.

---

## Features

**Semantic Vector Retrieval**
Documents uploaded to the engine are automatically cleaned, parsed into text blocks, mapped into a high-dimensional vector space, and safely stored on local disk media.

**Verified Source Citations**
Every single response from the assistant includes a list of verified reference tags along with mathematical similarity confidence scores, making the system transparent and auditable.

**Minimalist Access Card Aesthetic**
The user interface is designed around a premium, high-contrast brutalist design, featuring a functional virtual EMV smart card chip side-panel display mapping live model parameters.

**Asynchronous Performance & Autoscroll**
Built on FastAPI's native async loops paired with clean React `useRef` auto-scrolling triggers to make user conversation logs feel fluid and instantaneous.

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend UI** | Next.js 14+ (App Router), TypeScript, Tailwind CSS |
| **Backend API Gateway** | Python, FastAPI, Uvicorn, Pydantic |
| **Vector Database** | ChromaDB (Persistent Storage Engine Mode) |
| **Embedding Model** | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **Core AI Orchestrator** | Google GenAI SDK (Gemini 2.5 Flash) |

---

## Project Structure

```text
popclub-bot-v2/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI App Initialization
│   │   ├── config.py           # Pydantic BaseSettings management
│   │   ├── api/                # API Route Layer (Controllers)
│   │   │   ├── __init__.py
│   │   │   ├── chat.py         # Chat and streaming endpoints
│   │   │   └── admin.py        # File upload and re-indexing endpoints
│   │   ├── core/               # Core AI Engines (The Brains)
│   │   │   ├── __init__.py
│   │   │   ├── embedding.py    # Local SentenceTransformers wrapper
│   │   │   ├── vector_db.py    # ChromaDB interface
│   │   │   └── rag.py          # Context retrieval & prompt orchestration
│   │   ├── schemas/            # Pydantic Request/Response validation models
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   └── admin.py
│   │   └── services/           # Business Logic Layer
│   │       ├── __init__.py
│   │       └── document_parser.py # JSON, MD, and Text parsing logic
│   ├── requirements.txt        # Python Dependencies
│   └── .env            # Your Environmental variables
└── frontend/                  
```

---

## Installation & Local Setup

### Prerequisites

- Python 3.10 or higher installed on your machine
- Node.js v18 or higher with npm installed
- A Gemini API Key generated from [Google AI Studio](https://aistudio.google.com/)

### 1. Backend Core Setup

Open a terminal, navigate to the backend directory, and create an isolated virtual environment:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

- **Windows (CMD/PowerShell):** `.venv\Scripts\activate`
- **Mac/Linux:** `source .venv/bin/activate`

Install all necessary production-grade dependencies:

```bash
pip install -r requirements.txt
```

Create a file named exactly `.env` directly inside the `backend/` directory:

```
GEMINI_API_KEY="AIzaSyYourActualGeminiAPIKeyGoesHere"
```

Launch the backend API gateway using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The backend engine docs will now be serving at `http://localhost:8000/docs`.

### 2. Frontend Interface Setup

Open a separate terminal window (keep the backend server running) and move into the frontend directory:

```bash
cd frontend
npm install
```

Launch the Next.js local development workspace:

```bash
npm run dev
```

Open your browser and navigate to `http://localhost:3000` to view your app.

---

## Usage & Knowledge Base Ingestion

By default, the persistent vector database boots up empty. If you ask a question right away, the bouncer system will safely tell you it does not possess that knowledge. To seed the engine with the provided POPclub core context:

1. Go to the interactive Swagger UI panel at `http://localhost:8000/docs`.
2. Click to expand the green `POST /api/v1/admin/upload` endpoint segment.
3. Click the **"Try it out"** button.
4. Click **"Choose File"** and upload the template data file (you can paste the raw structural text below into a local file named `knowledge.txt`).
5. Click **"Execute"**.

The backend will chunk the document, run embedding loops, and save the vectorized indices directly onto your machine's local disk space inside `backend/chroma_db/`. You can now query your minimalist UI on port 3000 regarding team structures, POPcoin valuation vectors, or partner credit card tier offerings cleanly!

### Ingestion Data Sheet (`knowledge.txt`)

```text
POPclub (also known as POP UPI) is India's most rewarding UPI payment, shopping, and credit card app. Its legal name is Poptech Growth Private Limited. It combines fast UPI payments with a powerful rewards ecosystem where users earn POPcoins on every transaction which can be redeemed for shopping discounts, vouchers, and exclusive deals. POPclub was founded in May 2023 by Bhargav Errangi, a fintech and e-commerce professional who saw that UPI lacked a strong rewards ecosystem and built POP to fill that gap. The business head and nodal officer is Rajat Mittal, and senior engineering is led by Puneeth Uchil. POPclub has its registered office in Mumbai, Maharashtra, and its corporate office in Bengaluru, Karnataka. It is trusted by over 1 crore (10 million) users across India. The official website is https://popclub.co, and it operates in the fintech, e-commerce, and digital payments sectors.

Regarding POPcoins rewards rules: 1 POPcoin is always worth exactly 1 INR (1 POPcoin = ₹1, always). Users guaranteed earn 2% POPcoins on every UPI transfer to friends, family, or merchants. Users earn 5% back in POPcoins on every online transaction using the YES BANK POPclub Credit Card, and earn 2 POPcoins per 100 INR on offline spends. Popcoins redemption options include shopping on POPshop at up to 80% off on 500+ brands, or redeeming for gift vouchers from Zomato, Amazon, Swiggy, Myntra, Uber, Ola, and Zepto. Users can also partially convert coins to cashback where 10 POPcoins equals 1 INR, or explore curated deals under 999, 499, and 99 INR. POPcoins are valid for 365 days (1 year) from the date of credit and cannot be transferred between accounts. Users can check their balance by opening the POP app and tapping the coins section at the top right corner.

The core product is POP UPI, a super-fast and secure UPI payment platform. It allows users to scan any QR code, send or receive money instantly, and earn a guaranteed 2% POPcoins on every transaction with real-time notifications and industry-grade security on every transaction with zero joining fee.

Another major product is the YES BANK POPclub Credit Card. This is India's most rewarding RuPay credit card, exclusively for POP users. It is a lifetime free card with zero annual fees and zero joining fees as part of a limited-time offer, coming with 5,000 INR worth of joining and welcome benefits. It offers 5% back in POPcoins on every online transaction, 2 POPcoins per 100 INR on offline spends, and allows users to use credit on UPI via the POP platform. Users can manage the card and track offers directly inside the POP app. To apply, users download the POP app, complete their KYC, and apply directly inside the app.

The app features POPshop, an online rewards marketplace inside the POP app with 500+ curated D2C brands. Users can use POPcoins to shop at massive discounts between 60% to 80% off running all year round. Brands include Nike, Puma, boAt, NOISE, Foxtale, Snitch, and Portronics, alongside vouchers for Zomato, Swiggy, Amazon, Myntra, Uber, Ola, and Zepto. It features daily refreshed deals every 24 hours, POPminis trial-sized products, and zero-cost delivery on the first order.

The app also features a Refer and Earn program where users can refer friends to POP and earn 25 INR plus 100 POPcoins per successful referral.

The POP app is completely free to download and use. It can be downloaded on Android by searching 'POP' on the Google Play Store, or on iOS by searching 'POP' on the Apple App Store. POP uses industry-grade security for all transactions and has received TPAP approval from NPCI to operate as an official UPI application. It is partnered with YES Bank and Juspay for a robust, secure UPI infrastructure.
```

---

## API Reference

### `POST /api/v1/chat/query`

Queries the semantic vector space collection, extracts top contextual matches, and generates a grounded response.

**Request Payload Contract** (`application/json`)

```json
{
  "message": "What benefits come with the YES BANK card?",
  "history": []
}
```

**Response Payload Contract** (`200 OK`)

```json
{
  "answer": "The YES BANK POPclub Credit Card offers 5% back in POPcoins on every online transaction...",
  "citations": [
    {
      "source": "knowledge.txt",
      "text": "Another major product is the YES BANK POPclub Credit Card...",
      "score": 0.892
    }
  ]
}
```

---

**Repository Architecture:** [github.com/ritvikamin/popclub-copilot-v2](https://github.com/ritvikamin/popclub-copilot-v2)
