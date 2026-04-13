import json
import os

ANALYTICS_FILE = "analytics.json"


# =========================
# 📂 LOAD ANALYTICS
# =========================
def load_analytics():
    if not os.path.exists(ANALYTICS_FILE):
        return {
            "categories": {
                "Work": 0,
                "Personal": 0,
                "Promotions": 0,
                "Spam": 0
            }
        }

    with open(ANALYTICS_FILE, "r") as f:
        return json.load(f)


# =========================
# 💾 SAVE ANALYTICS
# =========================
def save_analytics(data):
    with open(ANALYTICS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =========================
# 📊 UPDATE CATEGORY COUNT
# =========================
def update_category_stats(category):
    data = load_analytics()

    if "categories" not in data:
        data["categories"] = {}

    if category not in data["categories"]:
        data["categories"][category] = 0

    data["categories"][category] += 1

    save_analytics(data)


# =========================
# 🧠 EMAIL CATEGORY LOGIC
# =========================
def categorize_email(subject, body):
    text = (subject + " " + body).lower()

    if any(word in text for word in ["offer", "sale", "discount", "deal"]):
        return "Promotions"

    elif any(word in text for word in ["meeting", "project", "deadline", "client"]):
        return "Work"

    elif any(word in text for word in ["family", "friend", "party", "home"]):
        return "Personal"

    elif any(word in text for word in ["win", "lottery", "free money", "urgent prize"]):
        return "Spam"

    else:
        return "Work"
    
# =========================
# 🚫 SPAM DETECTION
# =========================
def is_spam_email(subject, body):
    text = (subject + " " + body).lower()

    spam_keywords = [
        "win money", "free offer", "click here",
        "urgent response", "lottery", "claim now"
    ]

    return any(word in text for word in spam_keywords)