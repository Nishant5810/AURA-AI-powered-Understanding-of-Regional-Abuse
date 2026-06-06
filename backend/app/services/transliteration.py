import re
from typing import Tuple, Dict

# Standard dictionaries mapping Romanized regional slang/words to English translation/meanings
# This allows us to handle both classification normalization and phrase highlighting for the UI.

HINDI_TRANSLIT = {
    "ye": "this/these",
    "log": "people",
    "desh": "country",
    "ke": "of",
    "layak": "worthy",
    "nahi": "not",
    "gande": "dirty/bad",
    "hai": "is/are",
    "banda": "guy/person",
    "bahut": "very",
    "saale": "bastard (abusive)",
    "kamine": "scoundrel (abusive)",
    "chor": "thief",
    "gaddar": "traitor",
    "chutiya": "idiot/fool (abusive)",
    "fenko": "throw",
    "nikalo": "kick out",
    "maro": "beat/kill",
    "bhagao": "drive away",
    "randi": "whore (abusive)",
    "harami": "bastard (abusive)",
    "mulla": "muslim (derogatory in context)",
    "bhakt": "devotee (often political insult in context)",
    "pappu": "foolish/immature (political insult)",
    "deshdrohi": "anti-national",
}

TAMIL_TRANSLIT = {
    "ivan": "he/this guy",
    "avan": "he/that guy",
    "romba": "very",
    "mosamana": "bad/toxic",
    "aal": "person/guy",
    "waste": "useless/waste",
    "fellow": "guy/fellow",
    "da": "bro/dude",
    "oru": "a/one",
    "loosu": "crazy/foolish",
    "sava": "die",
    "olunga": "properly",
    "poda": "go away (mildly abusive)",
    "vella": "white/out",
    "ellam": "all",
    "worst": "worst",
    "paradesi": "wanderer/foreigner (abusive in context)",
    "poramboke": "wasteland (highly offensive caste/class slur)",
    "oolal": "corrupt",
    "thirudan": "thief",
    "kazhudhai": "donkey",
    "naaye": "dog (abusive)",
    "sombu": "sycophant",
}

TELUGU_TRANSLIT = {
    "veellu": "these people",
    "vallu": "those people",
    "mana": "our",
    "samajam": "society",
    "ki": "to",
    "problem": "problem",
    "andaru": "all",
    "waste": "useless",
    "naa": "my/our",
    "kodaka": "son of a (abusive)",
    "donga": "thief",
    "yedhava": "idiot/useless",
    "chavandi": "go die",
    "babu": "guy/boss",
    "lacha": "bribe",
    "thagalayya": "ruined",
    "chetha": "trash/garbage",
    "pichi": "mad/crazy",
    "nee": "your",
    "guddha": "ass (abusive)",
    "pichoda": "madman",
}

class TransliterationEngine:
    @staticmethod
    def identify_language_and_transliterate(text: str) -> Tuple[str, str, Dict[str, str]]:
        """
        Analyzes Romanized / English-mixed text, identifies if it's Hinglish, Tanglish, 
        Tenglish, or Standard Language, and provides a translated version.
        
        Returns:
            Tuple of (detected_language, normalized_text, translations_found)
        """
        # Clean text
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return "English", text, {}

        hindi_hits = 0
        tamil_hits = 0
        telugu_hits = 0
        
        translations = {}

        for w in words:
            if w in HINDI_TRANSLIT:
                hindi_hits += 1
                translations[w] = HINDI_TRANSLIT[w]
            if w in TAMIL_TRANSLIT:
                tamil_hits += 1
                translations[w] = TAMIL_TRANSLIT[w]
            if w in TELUGU_TRANSLIT:
                telugu_hits += 1
                translations[w] = TELUGU_TRANSLIT[w]

        # Scoring code-mixed/transliterated variants
        max_hits = max(hindi_hits, tamil_hits, telugu_hits)
        
        # Check script characters
        has_hindi_script = bool(re.search(r'[\u0900-\u097F]', text))
        has_tamil_script = bool(re.search(r'[\u0B80-\u0BFF]', text))
        has_telugu_script = bool(re.search(r'[\u0C00-\u0C7F]', text))

        if has_hindi_script:
            detected = "Hindi"
            normalized = text
        elif has_tamil_script:
            detected = "Tamil"
            normalized = text
        elif has_telugu_script:
            detected = "Telugu"
            normalized = text
        elif max_hits == 0:
            detected = "English"
            normalized = text
        else:
            # If Romanized
            if max_hits == hindi_hits:
                detected = "Hinglish (Hindi-English)"
            elif max_hits == tamil_hits:
                detected = "Tanglish (Tamil-English)"
            else:
                detected = "Tenglish (Telugu-English)"
            
            # Construct a normalized/glossed translation for internal semantic understanding
            words_normalized = []
            for w in text.split():
                clean_w = re.sub(r'[^\w]', '', w).lower()
                if clean_w in translations:
                    # Keep original word structure but append its context translation in brackets for model helper
                    words_normalized.append(f"{w} ({translations[clean_w]})")
                else:
                    words_normalized.append(w)
            normalized = " ".join(words_normalized)

        return detected, normalized, translations
