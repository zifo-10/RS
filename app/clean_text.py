import re
import pyarabic.araby as araby


def clean_arabic_text(text: str) -> str:
    # Normalize the text (handling variations like "ه" and "ة", "ى" and "ي")
    text = araby.normalize_teh(text)
    # text = araby.normalize_alef(text)
    # text = araby.normalize_hamza(text)

    # Convert final "ي" to "ى" at the end of words
    text = re.sub(r'ي\b', 'ى', text)

    # Convert "أ" to "ا"
    text = re.sub(r'أ', 'ا', text)

    # Convert "إ" (Hamza above ا) to "ا"
    text = re.sub(r'إ', 'ا', text)

    return text
