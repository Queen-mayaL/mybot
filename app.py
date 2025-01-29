from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

grocery_list = []  # Store grocery items
user_states = {}   # Track user states (e.g., adding an item)

@app.route("/")
def home():
    return "Your WhatsApp bot is running!"

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Handle incoming WhatsApp messages"""
    from_number = request.values.get("From", "").strip()  # Unique user identifier
    incoming_msg = request.values.get("Body", "").strip().lower()

    resp = MessagingResponse()
    msg = resp.message()

    # Check if user is in "Add Item" mode
    if user_states.get(from_number) == "adding_item":
        grocery_list.append(incoming_msg)  # ✅ Add the item to the list
        user_states[from_number] = None  # Reset state
        msg.body(f"✅ '{incoming_msg}' added to your grocery list!\n\nSend 'start' to see options again.")
        return str(resp)

    # Handle normal commands
    if incoming_msg == "start":
        return send_interactive_message()
    elif incoming_msg in ["view list", "list"]:
        return process_user_selection("view_list", from_number)
    elif incoming_msg in ["add item", "add"]:
        return process_user_selection("add_item", from_number)
    elif incoming_msg in ["clear list", "clear"]:
        return process_user_selection("clear_list", from_number)
    else:
        msg.body("I didn't understand that. Send 'start' to see options.")
        return str(resp)

def send_interactive_message():
    """Send an interactive message"""
    resp = MessagingResponse()
    msg = resp.message()
    
    msg.body("\U0001F6D2 What would you like to do?\n\n"
             "1️⃣ View List\n"
             "2️⃣ Add Item\n"
             "3️⃣ Clear List\n\n"
             "Reply with a number or command.")

    return str(resp)

def process_user_selection(selection, user):
    """Handle user's selection"""
    resp = MessagingResponse()
    msg = resp.message()

    if selection == "view_list":
        if grocery_list:
            items = "\n".join(grocery_list)
            msg.body(f"\U0001F6D2 Your Grocery List:\n{items}")
        else:
            msg.body("Your grocery list is empty. Send 'add' to add items.")
    
    elif selection == "add_item":
        msg.body("Please type the item you'd like to add.")
        user_states[user] = "adding_item"  # Set state to track the next message as an item

    elif selection == "clear_list":
        grocery_list.clear()
        msg.body("✅ Grocery list cleared!")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)