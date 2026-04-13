from flask import Flask, request, jsonify, Response
import os

from services.gmail_service import send_email, extract_emails_from_file
from agents.assistant_agent import (
    generate_ai_email,
    improve_email,
    personalize_email,
    chat_with_ai
)

from utils.analytics_manager import (
    categorize_email,
    update_category_stats,
    load_analytics,
    is_spam_email
)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return "🚀 AI Email Agent Live"


# =========================
# ✉️ AI EMAIL GENERATION
# =========================
@app.route("/ai/generate", methods=["POST"])
def generate_email():
    data = request.json

    email = generate_ai_email(
        data.get("prompt"),
        data.get("tone", "professional"),
        data.get("length", "medium"),
        data.get("language", "English"),
        data.get("user_id", "default")
    )

    return Response(email, mimetype="text/plain")


# =========================
# 🤖 AI CHATBOT
# =========================
@app.route("/ai/chat", methods=["POST"])
def ai_chat():
    message = request.json.get("message")
    return {"reply": chat_with_ai(message)}


# =========================
# 📧 SEND SINGLE EMAIL
# =========================
@app.route("/send-email", methods=["POST"])
def send_single_email():
    data = request.form if request.form else request.json

    to = data.get("to")
    subject = data.get("subject", "No Subject")
    body = data.get("body", "")

    if not to:
        return {"error": "Recipient required"}, 400

    category = categorize_email(subject, body)

    if is_spam_email(subject, body):
        update_category_stats("Spam")
        return {"status": "blocked", "reason": "spam detected"}

    update_category_stats(category)

    # 🔥 ATTACHMENT SUPPORT (SINGLE)
    attachment = request.files.get("attachment")

    result = send_email(to, subject, body, attachment)

    return {
        "status": result,
        "category": category
    }


# =========================
# 🚀 BULK SEND (UPDATED WITH ATTACHMENT)
# =========================
@app.route("/send-bulk", methods=["POST"])
def send_bulk():
    file = request.files.get("file")
    subject = request.form.get("subject")
    body = request.form.get("body")

    # 🔥 NEW: attachment support
    attachment = request.files.get("attachment")

    if not file:
        return {"error": "File required"}, 400

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    emails = extract_emails_from_file(path)

    sent, spam, failed = 0, 0, 0
    results = []

    # 🔥 IMPORTANT: read attachment ONCE
    attachment_data = None
    attachment_name = None
    attachment_type = None

    if attachment:
        attachment_data = attachment.read()
        attachment_name = attachment.filename
        attachment_type = attachment.content_type

    for email in emails:
        if is_spam_email(subject, body):
            spam += 1
            update_category_stats("Spam")
            results.append({"email": email, "status": "spam_blocked"})
            continue

        category = categorize_email(subject, body)
        update_category_stats(category)

        try:
            # 🔥 send email with attachment
            result = send_email(
                email,
                subject,
                body,
                attachment_data,
                attachment_name,
                attachment_type
            )

            if "sent" in result:
                sent += 1
            else:
                failed += 1

        except Exception as e:
            failed += 1
            result = f"error: {str(e)}"

        results.append({"email": email, "status": result})

    return {
        "total": len(emails),
        "sent": sent,
        "spam_blocked": spam,
        "failed": failed,
        "results": results
    }


# =========================
# 📊 ANALYTICS
# =========================
@app.route("/analytics/categories", methods=["GET"])
def get_categories():
    return jsonify(load_analytics().get("categories", {}))


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)