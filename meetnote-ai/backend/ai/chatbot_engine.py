
def ask_chatbot(question, transcript):

    question = question.lower()

    transcript = transcript.lower()

    if "meeting" in question:
        return "The meeting discussion is available in transcript."

    elif "summary" in question:
        return transcript[:300]

    elif "action" in question:
        return "Action items detected from meeting."

    elif "deadline" in question:
        return "Please check transcript for deadlines."

    else:
        return "AI chatbot response generated successfully."