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