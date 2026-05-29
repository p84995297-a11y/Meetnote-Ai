from fastapi import APIRouter
from pydantic import BaseModel

from ai.translator import translate_text

router = APIRouter()


class TranslationRequest(BaseModel):

    text: str

    language: str


@router.post("/translate")
async def translate(request: TranslationRequest):

    translated_text = translate_text(

        request.text,

        request.language

    )

    return {
        "translated_text": translated_text
    }