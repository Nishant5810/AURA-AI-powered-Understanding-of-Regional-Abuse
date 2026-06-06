import random
import datetime
from sqlalchemy.orm import Session
from app.models import EmergingSlang, RegionalTrend
from app.services.transliteration import HINDI_TRANSLIT, TAMIL_TRANSLIT, TELUGU_TRANSLIT

# List of mock emerging slang terms with their metadata
MOCK_EMERGING_SLANGS = [
    {"term": "opanna", "language": "Tenglish (Telugu-English)", "definition": "A slang used to mock self-righteous online posts.", "frequency": 145, "growth_rate": 210.5},
    {"term": "dumeel", "language": "Tanglish (Tamil-English)", "definition": "Offensive regional label targeting specific political/ideological groups in Tamil Nadu.", "frequency": 380, "growth_rate": 340.0},
    {"term": "libtardwa", "language": "Hinglish (Hindi-English)", "definition": "Derogatory political blend word used to target liberals in Hindi circles.", "frequency": 512, "growth_rate": 185.2},
    {"term": "unil", "language": "Tanglish (Tamil-English)", "definition": "Squirrel metaphor used as a political troll term for a ruling party supporter.", "frequency": 290, "growth_rate": 120.0},
    {"term": "chavata", "language": "Tenglish (Telugu-English)", "definition": "Slang for spineless or coward, emerging in Telugu political tweets.", "frequency": 95, "growth_rate": 80.0},
    {"term": "andhbhakt", "language": "Hinglish (Hindi-English)", "definition": "Communal/political slang targeting blind followers of political figures.", "frequency": 670, "growth_rate": 230.0},
    {"term": "sanghi", "language": "Hinglish (Hindi-English)", "definition": "Political label used derogatorily in national debate forums.", "frequency": 590, "growth_rate": 150.0},
    {"term": "congi", "language": "Hinglish (Hindi-English)", "definition": "Derogatory political shorthand for Congress party workers.", "frequency": 210, "growth_rate": 95.5},
    {"term": "vadaa", "language": "Tanglish (Tamil-English)", "definition": "A slang term used in gaming servers to label easy target players.", "frequency": 160, "growth_rate": 115.0}
]

# States map for regional heatmap simulation
INDIAN_STATES = [
    {"state": "Tamil Nadu", "language": "Tamil", "intensity": 42.5},
    {"state": "Andhra Pradesh", "language": "Telugu", "intensity": 35.2},
    {"state": "Telangana", "language": "Telugu", "intensity": 38.0},
    {"state": "Uttar Pradesh", "language": "Hindi", "intensity": 58.4},
    {"state": "Bihar", "language": "Hindi", "intensity": 61.2},
    {"state": "Delhi", "language": "Hindi", "intensity": 55.0},
    {"state": "Maharashtra", "language": "Hindi", "intensity": 28.5},
    {"state": "Karnataka", "language": "Telugu", "intensity": 22.0}
]

class SlangMonitorService:
    @staticmethod
    def seed_initial_slangs(db: Session):
        """Seed the emerging slang database with mock trending slangs if empty."""
        pass

    @staticmethod
    def seed_regional_trends(db: Session):
        """Seed the regional trend heatmap database if empty."""
        pass

    @staticmethod
    def simulate_social_feed_ingestion(db: Session):
        """
        Simulate polling social media comments.
        Randomly increments frequencies of existing emerging slangs and creates minor spikes.
        """
        slangs = db.query(EmergingSlang).all()
        if not slangs:
            SlangMonitorService.seed_initial_slangs(db)
            slangs = db.query(EmergingSlang).all()
            
        for slang in slangs:
            # Randomly increase frequency
            freq_inc = random.randint(5, 30)
            slang.frequency += freq_inc
            # Update growth rate
            slang.growth_rate = round(slang.growth_rate + random.uniform(-10.0, 25.0), 1)
            # Ensure growth rate stays positive/sensible
            slang.growth_rate = max(10.0, slang.growth_rate)
            slang.last_seen = datetime.datetime.utcnow()
            
        db.commit()
        return len(slangs)
