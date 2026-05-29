from deep_translator import GoogleTranslator


def translate_text(text, target_language):

    try:

        translated = GoogleTranslator(source='auto', target=target_language).translate(text)

        return translated

    except Exception as e:

        return str(e)