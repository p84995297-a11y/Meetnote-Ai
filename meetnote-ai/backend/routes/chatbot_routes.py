from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):

    question: str

    transcript: str


@router.post("/chatbot")
async def chatbot(request: ChatRequest):

    question = request.question.lower()

    transcript = request.transcript

    if "summary" in question:

        response = transcript[:500]

    elif "meeting" in question:

        response = "This meeting discussion is available in transcript."

    else:

        response = (
            "AI Chatbot Response:\n\n"
            + transcript[:1000]
        )

    return {

        "response": response

    }