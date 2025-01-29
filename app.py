from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Respond to incoming WhatsApp messages"""
    incoming_msg = request.values.get("Body", "").lower()
    resp = MessagingResponse()
    msg = resp.message()

    if "hello" in incoming_msg:
        msg.body("Hi! How can I help you?")
    elif "bye" in incoming_msg:
        msg.body("Goodbye! Have a great day.")
    else:
        msg.body("I'm not sure how to respond to that.")

    return str(resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)