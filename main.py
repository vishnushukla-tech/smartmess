from fastapi import FastAPI, Query, Response, Request

app = FastAPI()

# Verification token that matches what you put in Meta
VERIFY_TOKEN = "smartmess_secret_123"

@app.get("/")
def home():
    return {"message": "SmartMess Webhook Server is Live!"}

# Handshake endpoint for Meta Webhook verification
@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    return Response(content="Token mismatch", status_code=403)

# Receiver endpoint when students click buttons
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    print("Received student action:", data)
    return {"status": "ok"}