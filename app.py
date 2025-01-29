from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os

app = Flask(__name__)

grocery_list = []  # Store grocery items

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Handle incoming WhatsApp messages"""
    incoming_msg = request.values.get("Body", "").strip().lower()

    if incoming_msg == "start":
        return send_interactive_message()
    else:
        return process_user_selection(incoming_msg)

def send_interactive_message():
    """Send a message with interactive buttons"""
    response = {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "What would you like to do?"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "view_list",
                            "title": "📋 View List"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "add_item",
                            "title": "➕ Add Item"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "clear_list",
                            "title": "🗑️ Clear List"
                        }
                    }
                ]
            }
        }
    }
    return json.dumps(response)

def process_user_selection(selection):
    """Handle user's selection from buttons"""
    resp = MessagingResponse()
    msg = resp.message()

    if selection == "view_list":
        if grocery_list:
            items = "\n".join(grocery_list)
            msg.body(f"🛒 Your Grocery List:\n{items}")
        else:
            msg.body("Your grocery list is empty. Send 'add' to add items.")
    
    elif selection == "add_item":
        msg.body("Please type the item you'd like to add.")

    elif selection == "clear_list":
        grocery_list.clear()
        msg.body("✅ Grocery list cleared!")

    else:
        # If the user sends a message that is not recognized, assume it's an item
        grocery_list.append(selection)
        msg.body(f"Added '{selection}' to your grocery list. Send 'start' to see options again.")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
