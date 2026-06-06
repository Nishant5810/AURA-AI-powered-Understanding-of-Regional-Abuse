import re
from typing import Dict, Any, List

class ExplainabilityLayer:
    @staticmethod
    def get_token_highlights(text: str, toxic_phrases: List[str]) -> List[Dict[str, Any]]:
        """
        Tokenizes the input text and labels each token/phrase segment with a toxicity flag.
        This allows the frontend (React or Streamlit) to color-code toxic segments.
        
        Example output:
        [
            {"text": "Ye banda ", "is_toxic": False},
            {"text": "saale", "is_toxic": True},
            {"text": " bahut ganda hai", "is_toxic": False}
        ]
        """
        if not toxic_phrases:
            return [{"text": text, "is_toxic": False}]

        # Sort toxic phrases by length descending to match larger chunks first
        sorted_phrases = sorted(toxic_phrases, key=len, reverse=True)
        
        # Build regex pattern matching any of the toxic phrases
        escaped_phrases = [re.escape(p) for p in sorted_phrases if p.strip()]
        if not escaped_phrases:
            return [{"text": text, "is_toxic": False}]

        pattern = "|".join(escaped_phrases)
        
        # Split text by toxic phrases, keeping the matches
        parts = re.split(f"({pattern})", text, flags=re.IGNORECASE)
        
        highlighted_tokens = []
        for part in parts:
            if not part:
                continue
            
            # Check if this part is one of the toxic phrases (case-insensitive)
            is_toxic = any(part.lower() == p.lower() or p.lower() in part.lower() for p in sorted_phrases)
            
            highlighted_tokens.append({
                "text": part,
                "is_toxic": is_toxic
            })
            
        return highlighted_tokens

    @staticmethod
    def enrich_explanation(classification_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches the reasoning with structural descriptions of the flagged categories.
        """
        result = classification_result.copy()
        toxic_phrases = result.get("toxic_phrases", [])
        
        # Get token level highlights
        result["highlights"] = ExplainabilityLayer.get_token_highlights(
            result["input_text"], 
            toxic_phrases
        )
        
        return result
