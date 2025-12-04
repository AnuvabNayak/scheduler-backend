# 📅 WhatsApp Scheduler Backend

A FastAPI + SQLModel backend for handling WhatsApp webhooks, lead creation, appointment scheduling, and automated WhatsApp messaging using the WhatsApp Cloud API.

---

## 🚀 Features

- 📩 WhatsApp webhook receiver  
- 🤖 Automated WhatsApp replies (Cloud API)  
- 🧾 Lead & appointment management  
- 🕒 Time-window selection (Morning / Afternoon / Evening)  
- ⚡ Fully async — FastAPI + SQLModel + asyncpg  
- 🔒 Webhook signature verification (HMAC SHA256)  
- 🧱 Clean architecture with routers, CRUD, models, and DB layers  

---

## 📂 Project Structure

```
backend/
│── main.py
│── database.py
│── models.py
│── schemas.py
│── crud.py
│── webhook.py
│── scheduling.py
│── requirements.txt
│── .env.example
└── README.md
```

---

## ⚙️ Requirements

- Python 3.10+
- PostgreSQL
- WhatsApp Cloud API credentials
- Meta App Secret (for webhook signature validation)
- Virtual environment recommended

---

## 🔧 Installation

### **1️⃣ Clone the repository**
```bash
git clone https://github.com/AnuvabNayak/scheduler-backend.git
cd scheduler-backend
```

### **2️⃣ Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate      # Mac / Linux
venv\Scripts\activate         # Windows
```

### **3️⃣ Install dependencies**
```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file using the following structure (real secrets should NOT be committed):

```
# Environment
ENV=development
FRONTEND_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE_NAME

# WhatsApp Cloud API
WHATSAPP_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_ID=your_whatsapp_phone_id
APP_SECRET=your_meta_app_secret

# Development only
DISABLE_SIGNATURE_VERIFICATION=true
```

> ⚠️ Commit only `.env.example`, not your real `.env`.

---

## ▶️ Running the Server

Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

### Access the API Docs:
- Swagger UI → http://localhost:8000/docs  
- ReDoc → http://localhost:8000/redoc  

---

## 📬 WhatsApp Webhook URL

When deployed, set your webhook to:

```
POST https://your-domain.com/webhook
```

The backend:
- Validates signature  
- Parses incoming message  
- Creates/updates Lead  
- Creates Appointment  
- Sends WhatsApp reply  

---

## 📆 Scheduling API

### **POST /scheduling/select-window**

**Request:**
```json
{
  "appointment_id": "uuid-here",
  "date_str": "2025-02-10",
  "window": "MORNING"
}
```

**Response:**  
Updated Appointment object with new time window.

---

## 🧠 Business Logic Overview

### When a customer messages on WhatsApp:
1. Webhook receives the message  
2. Lead is created or fetched  
3. Appointment is created  
4. Automated message sent with scheduling link  

### When user selects a time window:
- Validates date is not in the past  
- Rejects changes after confirmation  
- Updates preferred date + time window  
- Updates status  

---

## 🛡 Security Features

- HMAC SHA256 webhook signature validation  
- `.env` excluded via `.gitignore`  
- UUIDs for all primary keys  
- Validation for scheduling logic  

---

## 🚀 Deployment

Compatible with:

- Render  
- Railway  
- Docker / Docker Compose  
- AWS / Azure / GCP  
- Heroku (with Postgres add-on)

Use this as your start command:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🤝 Contributing

1. Fork the repo  
2. Create a new branch  
3. Make your changes  
4. Open a pull request  

---

## ⭐ Author

**Anuvab Bikash Nayak**  
GitHub: https://github.com/AnuvabNayak  
LinkedIn: https://www.linkedin.com/in/anuvab-nayak-4baba5134/

---
