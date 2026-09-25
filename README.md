# Comment2DM

Comment2DM is a SaaS-style Instagram DM automation app for multiple customers using one Meta app.

## Architecture

Customer A ──┐
Customer B ──┤
Customer C ──┼──> ONE Meta app
Customer D ──┤
Customer E ──┘
            │
            ▼
      OAuth / Tokens
            │
            ▼
       YOUR FastAPI
            │
      ┌─────┴───────┐
      ▼             ▼
   Campaigns     Webhooks
      │             │
      └──────┬──────┘
             ▼
         Instagram
             │
             ▼
    Interactive React UI

## How it works

1. A user registers or logs in to the app.
2. They connect their Instagram Business account.
3. The server stores their Instagram access token for that user.
4. The user creates a campaign with a keyword, product URL, and DM message.
5. A webhook receives comments or related Instagram events.
6. If a comment matches a campaign keyword, the server sends a DM.

## Project layout

- backend/ - FastAPI server and authentication logic
- frontend/frontend - React + Vite UI

## Local setup

1. Copy `.env.example` to `.env` in the backend folder.
2. Fill in your real Meta app values.
3. Start the backend:
   cd backend
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
4. Start the frontend:
   cd frontend/frontend
   npm start
5. Open http://127.0.0.1:5173

## Required Meta config

To fully automate Instagram DMs, you must have:

- a Meta developer app
- an Instagram Business account
- OAuth configured with a valid redirect URL
- a public HTTPS callback for webhook verification
- webhook subscriptions enabled for the relevant Instagram events

## Important note

The app is ready for your SaaS architecture, but Instagram automation depends on real Meta app credentials and a public HTTPS endpoint. Localhost cannot receive Meta webhook callbacks.

For local testing, use ngrok or another tunnel to expose your backend over HTTPS.
