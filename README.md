# AI Sales Assistant (Contact Digitization Platform)

An end-to-end AI-powered CRM digitization platform that uses computer vision and natural language processing to extract, enrich, and save business card contacts into a Google Sheet while providing real-time WhatsApp notifications to managers. 

This platform uses **LangGraph** for resilient stateful workflow orchestration and **Gemini 2.5 Flash Lite** for both vision (image OCR) and native multimodal audio transcription.

---

## 🏗 Architectural Overview (LangGraph Agent)

The core logic of the AI Sales Assistant is orchestrated via a fully stateful, cyclic graph built on **LangGraph**. It utilizes a finite state machine to manage human-in-the-loop interactions.

### Agent Workflow (Node by Node)
1. **`process_input`**: The router node. It reads the incoming message from the React UI. If it's an image, it routes to `extract_vision`. If audio, to `process_audio`. If text, it evaluates whether the user is confirming a pending extraction or simply chatting.
2. **`extract_vision`**: Receives a Base64 encoded image of a business card. Leverages Gemini 2.5 Flash Lite (with structured Pydantic outputs and cascading fallbacks) to extract Name, Company, Email, and Phone.
3. **`deduplicate_contact`**: Connects to Google Sheets and checks if the extracted email or phone number already exists in the CRM. If a duplicate is found, the graph gracefully halts and notifies the user.
4. **`enrich_contact`**: Using the extracted company name, the agent performs a secondary LLM inference to automatically find or guess the company's official Website and LinkedIn profile URL.
5. **`save_to_sheets`**: Pauses the graph to await human confirmation. Once approved by the user, this node appends the structured data (including enriched URLs) to the Google Sheet.
6. **`send_whatsapp`**: Fires a WhatsApp notification to the assigned manager alerting them of the newly saved contact via the Meta/Twilio Business API.
7. **`process_audio`**: An asynchronous side-loop. Listens to Base64 audio voice notes, natively transcribes them using Gemini's multimodal engine, summarizes the context, and attaches the transcript to the saved contact in the database.

**Checkpointing**: The entire LangGraph state is persisted using a local `MongoDB` instance. This guarantees that if the server crashes while awaiting human approval, the state is preserved and the session resumes seamlessly.

---

## ⚙️ Environment Variables Setup

Before running the project, you must set up your credentials. In the `backend` directory, duplicate the `.env.example` file and rename it to `.env`. 

```env
# MongoDB (Leave as is for local Docker deployment)
MONGODB_URL=mongodb://mongo:27017

# Google AI Core (Gemini)
GOOGLE_API_KEY=your_gemini_api_key_here

# Google Sheets Configuration
GOOGLE_SHEET_ID=your_spreadsheet_id_here
GOOGLE_SHEETS_CREDENTIALS={"type":"service_account", ...} # Minified JSON string

# WhatsApp Business API (Meta Developer Portal or Twilio Sandbox)
WHATSAPP_TOKEN=your_whatsapp_bearer_token
WHATSAPP_PHONE_ID=your_whatsapp_phone_number_id
WHATSAPP_MANAGER_PHONE=+1234567890
```

### Note on Google Sheets:
Ensure your target Google Sheet has been "Shared" with the `client_email` address found inside your `GOOGLE_SHEETS_CREDENTIALS` JSON. The system will automatically generate header columns if the sheet is empty.

---

## 🚀 Build, Run, and Test Locally

This project is fully containerized using Docker, allowing you to run the frontend, backend, and MongoDB checkpointer simultaneously with a single command.

### Prerequisites:
- Docker Desktop installed and running.

### 1. Build and Run the Containers
Open your terminal at the root of the project and execute:
```bash
docker compose up --build
```
This command will pull the necessary images, install all Python/Node dependencies, compile the Vite frontend using SWC, and start the local network.

### 2. Access the Platform
- **Frontend (React UI)**: Open your browser to `http://localhost:5173`
- **Backend (FastAPI)**: Open your browser to `http://localhost:8000/docs` to view the interactive Swagger API documentation.

### 3. Testing the Workflow
1. Open the Frontend UI.
2. Drag and drop a business card image into the chat input.
3. Wait for the agent to extract the text and enrich the data.
4. Review the returned payload. Type "Yes" to approve.
5. Check your Google Sheet to verify the new row has been appended!
6. Click the microphone icon to record a voice note, and verify the transcript is attached to the spreadsheet row.

---

## ☁️ Deployment Guide

Because the application is stateless at the container level and relies on MongoDB for state management, it is perfectly suited for modern cloud hosting.

### 1. Deploying the Backend (GCP Cloud Run)
Google Cloud Run is highly recommended for the FastAPI backend as it scales to zero.
1. Authenticate with GCP CLI: `gcloud auth login`
2. Submit the backend build to Google Artifact Registry.
3. Deploy the container:
   ```bash
   gcloud run deploy ai-sales-backend \
     --source ./backend \
     --port 8000 \
     --set-env-vars MONGODB_URL="your_atlas_uri",GOOGLE_API_KEY="..." \
     --allow-unauthenticated
   ```
*(Ensure you use a MongoDB Atlas URI for production instead of the local Docker network).*

### 2. Deploying the Frontend (Vercel / Netlify)
1. Navigate to your hosting provider (e.g., Vercel).
2. Link your Git repository and set the Root Directory to `frontend`.
3. Set the Framework Preset to `Vite`.
4. Add an environment variable `VITE_API_URL` pointing to your newly deployed Cloud Run backend URL.
5. Click **Deploy**.

Your AI Sales Assistant is now live and globally accessible!
