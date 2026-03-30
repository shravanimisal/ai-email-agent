import os
import google.generativeai as genai

# ✅ Configure API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_ai_email(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(
            f"Write a professional email for the following request:\n{prompt}"
        )

        return response.text

    except Exception as e:
        return f"❌ AI Error: {str(e)}"