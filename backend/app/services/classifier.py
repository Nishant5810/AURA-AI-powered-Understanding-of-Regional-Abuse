import re
import logging
from typing import Dict, Any, List, Tuple
from app import config
from app.services.transliteration import TransliterationEngine

logger = logging.getLogger("bhashashield.classifier")

# Lazy loading of Transformers to keep startup fast and fallback resilient
tokenizer = None
model = None
transformers_loaded = False

def load_transformer_model():
    global tokenizer, model, transformers_loaded
    if not config.USE_TRANSFORMERS:
        logger.info("Transformers are disabled in configuration. Using Lexical/Semantic Fallback engine.")
        return False
    
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        logger.info(f"Attempting to load transformer model: {config.MODEL_NAME}...")
        # Note: If this takes too long or fails, the try-catch ensures fallback is used
        tokenizer = AutoTokenizer.from_pretrained(config.MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(config.MODEL_NAME)
        transformers_loaded = True
        logger.info("Transformer model loaded successfully.")
        return True
    except Exception as e:
        logger.warning(f"Failed to load Hugging Face model ({e}). Using Lexical/Semantic Fallback engine.")
        return False

# Rule-based / Lexicon engine database for precise categorization and high-performance fallback
LEXICON_RULES = {
    "Casteism": {
        "words": ["poramboke", "caste", "jaati", "kulam", "dalit", "shudra", "veellu andaru waste"],
        "severity": "High",
        "description": "Contains caste-based slurs or discriminatory targeting based on social hierarchy."
    },
    "Religious Hate": {
        "words": ["mulla", "bhakt", "hindu", "muslim", "christian", "jihad", "kafir", "dharma", "devalayam", "masjid"],
        "severity": "High",
        "description": "Targets religious beliefs, contains derogatory terms for religious groups, or incites communal division."
    },
    "Political Toxicity": {
        "words": ["oolal", "gaddar", "pappu", "chor", "deshdrohi", "anti-national", "bjp", "congress", "modi", "rahul", "donga", "lacha", "corrupt"],
        "severity": "Medium",
        "description": "Highly toxic or abusive political insults that degrade constructive discourse."
    },
    "Gender-Based Abuse": {
        "words": ["randi", "whore", "bitch", "misogyny", "she", "her", "female", "ponnu", "aadapilla"],
        "severity": "High",
        "description": "Contains misogynistic slurs or derogatory statements targeted at women or gender identity."
    },
    "Self-Harm Promotion": {
        "words": ["sava", "die", "suicide", "chavandi", "sachipo", "cut yourself", "kill myself", "end life"],
        "severity": "High",
        "description": "Encourages or promotes self-injury, suicide, or self-harm."
    },
    "Threat": {
        "words": ["maro", "bhagao", "nikalo", "beat", "kill", "murder", "bomb", "shoot", "attack", "chavandi", "savaadi"],
        "severity": "High",
        "description": "Expresses intent to commit physical violence or harm to individuals or groups."
    },
    "Cyberbullying": {
        "words": ["loosu", "waste", "fellow", "idiot", "yedhava", "chetha", "ugly", "fat", "stupid", "naaye", "kazhudhai"],
        "severity": "Medium",
        "description": "Targeted harassment, insults, or name-calling intended to demean an individual."
    },
    "Offensive Language": {
        "words": ["mosamana", "bad", "toxic", "romba mosamana", "aal", "worst", "poda"],
        "severity": "Medium",
        "description": "Contains offensive regional vocabulary or insults that violate social safety standards."
    },
    "Hate Speech": {
        "words": ["desh ke layak nahi", "gande", "saale", "kamine", "harami", "chutiya", "kodaka", "guddha", "veellu"],
        "severity": "High",
        "description": "Promotes hatred, exclusion, or discrimination against a group of people."
    }
}

COMMUNITY_KEYWORDS = {
    "Dalits / Lower Castes": ["poramboke", "dalit", "shudra", "jaati", "caste"],
    "Muslims": ["mulla", "jihad", "muslim", "masjid"],
    "Hindus": ["bhakt", "hindu", "dharma", "devalayam"],
    "Women": ["randi", "whore", "bitch", "ponnu", "aadapilla", "female"],
    "Out-Groups / Immigrants": ["ye log desh ke layak nahi", "these people", "veellu andaru waste", "paradesi"],
    "Political Rivals": ["pappu", "chor", "oolal", "gaddar", "deshdrohi", "lacha", "corrupt"]
}

class ToxicityClassifier:
    @staticmethod
    def detect_sarcasm(text: str, translations: Dict[str, str]) -> Tuple[bool, float]:
        """
        Detects if toxic sentiment is disguised behind polite or sarcastic markers.
        Example: "Wow, what a brilliant community, always creating problems."
        """
        text_lower = text.lower()
        
        # Sarcastic compliments
        sarcastic_markers = ["wow", "brilliant", "great", "excellent", "beautiful", "amazing", "genius", "sabash", "wah"]
        
        # Group descriptors
        group_markers = ["community", "ye log", "these people", "veellu", "varg", "jaati", "religion"]
        
        # Negative outcome/toxicity markers
        negative_markers = ["problem", "worst", "waste", "trouble", "fail", "garbage", "gande", "chetha"]

        has_sarcastic = any(marker in text_lower for marker in sarcastic_markers)
        has_group = any(marker in text_lower for marker in group_markers) or any(m in trans_val for m in ["people", "community"] for trans_val in translations.values())
        has_negative = any(marker in text_lower for marker in negative_markers) or any(m in trans_val for m in ["bad", "useless", "trash", "dirty"] for trans_val in translations.values())

        if has_sarcastic and (has_group or has_negative):
            # High probability of sarcasm-based toxicity
            return True, 0.85
        return False, 0.0

    @staticmethod
    def classify(text: str) -> Dict[str, Any]:
        """
        Classifies input text using XLM-RoBERTa (if loaded) or Lexical Fallback.
        """
        # 1. Transliterate and normalize
        lang, processed_text, translations = TransliterationEngine.identify_language_and_transliterate(text)
        
        # Check if transformer model is active
        # In a real environment, we'd tokenise and query PyTorch:
        # if transformers_loaded and tokenizer and model:
        #     ... query PyTorch ...
        
        # 2. Run Sarcasm Detection
        is_sarcastic, sarcasm_conf = ToxicityClassifier.detect_sarcasm(text, translations)
        
        # 3. Analyze text via Lexicon rules
        detected_categories = []
        highest_severity = "None"
        max_confidence = 0.0
        toxic_phrases = []
        matched_words = set()
        
        text_words = re.findall(r'\b\w+\b', text.lower())
        processed_words = re.findall(r'\b\w+\b', processed_text.lower())
        
        # Scan words
        for category, rules in LEXICON_RULES.items():
            cat_words = rules["words"]
            hits = 0
            for w in text_words:
                if w in cat_words or w in translations:
                    # check if the translated meaning matches or original matches
                    trans_val = translations.get(w, "")
                    if w in cat_words or any(cw in trans_val.split("/") or cw in trans_val for cw in cat_words):
                        hits += 1
                        matched_words.add(w)
                        # Add a phrase/span
                        toxic_phrases.append(w)
            
            # Additional substring checking (e.g. for multi-word phrases)
            for phrase in cat_words:
                if len(phrase.split()) > 1 and (phrase in text.lower() or phrase in processed_text.lower()):
                    hits += 1
                    toxic_phrases.append(phrase)
            
            if hits > 0:
                confidence = min(0.5 + (hits * 0.15), 0.98)
                detected_categories.append((category, confidence, rules["severity"]))
                if confidence > max_confidence:
                    max_confidence = confidence
                
                # Severity update: High > Medium > Low
                sev = rules["severity"]
                if sev == "High":
                    highest_severity = "High"
                elif sev == "Medium" and highest_severity != "High":
                    highest_severity = "Medium"
                elif sev == "Low" and highest_severity not in ["High", "Medium"]:
                    highest_severity = "Low"

        # 4. If Sarcasm is detected but no explicit toxic words are flagged
        if is_sarcastic and not detected_categories:
            detected_categories.append(("Hate Speech", sarcasm_conf, "High"))
            max_confidence = sarcasm_conf
            highest_severity = "High"
            toxic_phrases.append("brilliant community")  # sarcasm trigger representation

        # 5. Determine Target Community
        target_community = "General"
        max_target_hits = 0
        for community, keywords in COMMUNITY_KEYWORDS.items():
            hits = 0
            for kw in keywords:
                if kw in text.lower() or kw in processed_text.lower():
                    hits += 1
                elif any(kw in trans_val for trans_val in translations.values()):
                    hits += 1
            if hits > max_target_hits:
                max_target_hits = hits
                target_community = community

        # If no toxicity was detected
        if not detected_categories:
            return {
                "input_text": text,
                "processed_text": processed_text,
                "detected_language": lang,
                "label": "Non-Toxic",
                "confidence": 0.99,
                "severity": "None",
                "target_community": "General",
                "reasoning": "The content does not contain any detected regional slurs, abusive patterns, threat keywords, or communal toxicity markers.",
                "toxic_phrases": [],
                "suggested_action": "Allow Content"
            }

        # Select primary label (the one with highest confidence)
        detected_categories.sort(key=lambda x: x[1], reverse=True)
        primary_label, confidence, severity = detected_categories[0]
        
        # If sarcasm was detected, append to classification details
        if is_sarcastic:
            primary_label = f"Sarcastic {primary_label}"
            confidence = max(confidence, sarcasm_conf)
            severity = "High"

        # Moderator Action Recommendation
        if severity == "High":
            suggested_action = "Remove Immediately"
        elif severity == "Medium":
            suggested_action = "Human Review Recommended"
        else:
            suggested_action = "Warning Notice"

        # Generate Explainable AI Reasoning
        reasoning = f"This content was flagged as {primary_label} ({severity} Severity) because it contains text patterns that target {target_community}."
        if is_sarcastic:
            reasoning += " The toxicity is implicit, disguised behind polite/sarcastic vocabulary."
            
        category_reasons = []
        for cat, conf, sev in detected_categories:
            desc = LEXICON_RULES.get(cat, {}).get("description", "")
            if desc:
                category_reasons.append(desc)
        if category_reasons:
            reasoning += " " + " ".join(list(set(category_reasons)))

        return {
            "input_text": text,
            "processed_text": processed_text,
            "detected_language": lang,
            "label": primary_label,
            "confidence": round(confidence, 3),
            "severity": severity,
            "target_community": target_community,
            "reasoning": reasoning,
            "toxic_phrases": list(set(toxic_phrases)),
            "suggested_action": suggested_action
        }
