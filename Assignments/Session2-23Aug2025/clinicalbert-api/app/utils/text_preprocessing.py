"""Text preprocessing utilities for clinical text"""

import re
import string
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TextPreprocessor:
    """Text preprocessing for clinical notes"""
    
    def __init__(self):
        # Medical abbreviations and their expansions
        self.medical_abbreviations = {
            'pt': 'patient',
            'pts': 'patients', 
            'hx': 'history',
            'dx': 'diagnosis',
            'tx': 'treatment',
            'rx': 'prescription',
            'sx': 'symptoms',
            'w/': 'with',
            'w/o': 'without',
            'c/o': 'complains of',
            'r/o': 'rule out',
            's/p': 'status post',
            'nkda': 'no known drug allergies',
            'sob': 'shortness of breath',
            'cp': 'chest pain',
            'abd': 'abdomen',
            'ext': 'extremities',
            'neuro': 'neurological',
            'psych': 'psychiatric',
            'gi': 'gastrointestinal',
            'gu': 'genitourinary',
            'cv': 'cardiovascular',
            'resp': 'respiratory',
            'ent': 'ear nose throat',
            'heent': 'head eyes ears nose throat',
            'ms': 'musculoskeletal',
            'derm': 'dermatological'
        }
        
        # Common medical units
        self.medical_units = [
            'mg', 'mcg', 'g', 'kg', 'ml', 'l', 'units', 'iu',
            'mmhg', 'bpm', 'rpm', 'celsius', 'fahrenheit',
            'mg/dl', 'mmol/l', 'meq/l', 'pg/ml', 'ng/ml'
        ]
        
        # PHI patterns to anonymize
        self.phi_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),  # SSN
            (r'\b\d{10,11}\b', '[PHONE]'),  # Phone numbers
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # Email
            (r'\b\d{1,2}/\d{1,2}/\d{2,4}\b', '[DATE]'),  # Dates
            (r'\b\d{4}-\d{2}-\d{2}\b', '[DATE]'),  # ISO dates
        ]
    
    def preprocess_clinical_text(self, text: str, anonymize_phi: bool = True) -> str:
        """
        Preprocess clinical text for ClinicalBERT
        
        Args:
            text: Raw clinical text
            anonymize_phi: Whether to anonymize PHI
            
        Returns:
            Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Anonymize PHI if requested
        if anonymize_phi:
            text = self._anonymize_phi(text)
        
        # Expand medical abbreviations
        text = self._expand_abbreviations(text)
        
        # Normalize medical units
        text = self._normalize_units(text)
        
        # Clean special characters but preserve medical notation
        text = self._clean_special_characters(text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[,]{2,}', ',', text)
        
        return text.strip()
    
    def _anonymize_phi(self, text: str) -> str:
        """Anonymize potential PHI in text"""
        for pattern, replacement in self.phi_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text
    
    def _expand_abbreviations(self, text: str) -> str:
        """Expand medical abbreviations"""
        words = text.split()
        expanded_words = []
        
        for word in words:
            # Remove punctuation for matching
            clean_word = word.strip(string.punctuation)
            
            if clean_word in self.medical_abbreviations:
                # Replace with expansion, preserving punctuation
                expansion = self.medical_abbreviations[clean_word]
                if word != clean_word:
                    # Preserve punctuation
                    punctuation = word[len(clean_word):]
                    expanded_words.append(expansion + punctuation)
                else:
                    expanded_words.append(expansion)
            else:
                expanded_words.append(word)
                
        return ' '.join(expanded_words)
    
    def _normalize_units(self, text: str) -> str:
        """Normalize medical units"""
        # Standardize unit formatting
        for unit in self.medical_units:
            # Add space before unit if missing
            pattern = r'(\d)(' + re.escape(unit) + r')\b'
            text = re.sub(pattern, r'\1 \2', text, flags=re.IGNORECASE)
            
        return text
    
    def _clean_special_characters(self, text: str) -> str:
        """Clean special characters while preserving medical notation"""
        # Preserve medical notation like "+" and "-" in context
        # Remove excessive special characters
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\+\-$$$$\[\]\/\%]', ' ', text)
        
        # Normalize spacing around punctuation
        text = re.sub(r'\s*([\.,:;!?])\s*', r'\1 ', text)
        text = re.sub(r'\s*([()[\]])\s*', r' \1 ', text)
        
        return text
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract common clinical note sections
        
        Args:
            text: Clinical note text
            
        Returns:
            Dictionary of sections
        """
        sections = {}
        
        # Common section headers
        section_patterns = {
            'chief_complaint': r'(?:chief complaint|cc):\s*(.*?)(?=\n\w+:|$)',
            'history_present_illness': r'(?:history of present illness|hpi):\s*(.*?)(?=\n\w+:|$)',
            'past_medical_history': r'(?:past medical history|pmh):\s*(.*?)(?=\n\w+:|$)',
            'medications': r'(?:medications|meds):\s*(.*?)(?=\n\w+:|$)',
            'allergies': r'(?:allergies|nkda):\s*(.*?)(?=\n\w+:|$)',
            'social_history': r'(?:social history|sh):\s*(.*?)(?=\n\w+:|$)',
            'family_history': r'(?:family history|fh):\s*(.*?)(?=\n\w+:|$)',
            'review_of_systems': r'(?:review of systems|ros):\s*(.*?)(?=\n\w+:|$)',
            'physical_exam': r'(?:physical exam|pe|examination):\s*(.*?)(?=\n\w+:|$)',
            'assessment_plan': r'(?:assessment and plan|a&p|assessment|plan):\s*(.*?)(?=\n\w+:|$)',
            'impression': r'(?:impression|imp):\s*(.*?)(?=\n\w+:|$)'
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()
                
        return sections
    
    def clean_for_embedding(self, text: str) -> str:
        """
        Clean text specifically for embedding generation
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text optimized for embeddings
        """
        # Basic preprocessing
        text = self.preprocess_clinical_text(text)
        
        # Remove section headers
        text = re.sub(r'^[A-Z\s]+:', '', text, flags=re.MULTILINE)
        
        # Remove excessive newlines
        text = re.sub(r'\n+', ' ', text)
        
        # Remove very short words (likely artifacts)
        words = text.split()
        words = [word for word in words if len(word) > 1]
        
        return ' '.join(words)
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences for processing
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting for clinical text
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter very short sentences
                cleaned_sentences.append(sentence)
                
        return cleaned_sentences
