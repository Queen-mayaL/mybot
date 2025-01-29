from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocery.db'
db = SQLAlchemy(app)

class GroceryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Ensure database tables are created within the app context
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "Twilio WhatsApp bot is running!", 200

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip().lower()
    interactive_response = request.values.get('ButtonPayload', '')

    resp = MessagingResponse()
    msg = resp.message()

    # Step 1: Send interactive buttons when user says "hi"
    if incoming_msg == "hi":
        buttons = {
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "📋 Select an option:"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "show_list", "title": "✅ Show List"}},
                        {"type": "reply", "reply": {"id": "add_item", "title": "➕ Add"}},
                        {"type": "reply", "reply": {"id": "delete_item", "title": "❌ Delete"}}
                    ]
                }
            }
        }
        msg.media(json.dumps(buttons))  # Send buttons as JSON (Twilio Interactive API)

    # Step 2: If the user selects an option
    elif interactive_response == "show_list":
        items = GroceryItem.query.all()
        if items:
            item_list = '\n'.join([f"🛒 {item.id}. {item.name}" for item in items])
            msg.body(f"*Your Grocery List:*\n\n{item_list}")
        else:
            msg.body("🛒 Your grocery list is empty.")

    elif interactive_response == "add_item":
        msg.body("➕ What would you like to add? Type the item name.")

    elif interactive_response == "delete_item":
        msg.body("❌ Which item number do you want to delete? Type the number.")

    # Step 3: If the user types after selecting "Add" or "Delete"
    elif incoming_msg.startswith("add "):
        item_name = incoming_msg[4:].strip()
        if item_name:
            new_item = GroceryItem(name=item_name)
            db.session.add(new_item)
            db.session.commit()
            msg.body(f"✅ *Added:* '{item_name}' to your grocery list.")
        else:
            msg.body("⚠️ Please specify an item to add.")

    elif incoming_msg.startswith("delete "):
        try:
            item_id = int(incoming_msg[7:].strip())
            item = GroceryItem.query.get(item_id)
            if item:
                db.session.delete(item)
                db.session.commit()
                msg.body(f"❌ *Deleted:* '{item.name}' from your list.")
            else:
                msg.body("⚠️ Item not found.")
        except ValueError:
            msg.body("⚠️ Please provide a valid item number to delete.")

    else:
        msg.body("⚠️ Please select an option using the buttons.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
