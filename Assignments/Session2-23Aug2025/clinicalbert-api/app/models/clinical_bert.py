"""ClinicalBERT Model Integration for Healthcare NLP Tasks"""

import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    AutoModelForTokenClassification, pipeline
)
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
import asyncio
from pathlib import Path
import pickle
import json
from datetime import datetime
import re

from app.core.config import settings
from app.utils.text_preprocessing import TextPreprocessor

logger = logging.getLogger(__name__)

class ClinicalBERTModel:
    """ClinicalBERT model wrapper for healthcare NLP tasks"""
    
    def __init__(self):
        self.model_name = settings.MODEL_NAME
        self.cache_dir = Path(settings.MODEL_CACHE_DIR)
        self.max_length = settings.MAX_SEQUENCE_LENGTH
        self.batch_size = settings.BATCH_SIZE
        
        # Model components
        self.tokenizer = None
        self.base_model = None
        self.readmission_model = None
        self.ner_model = None
        self.embedding_model = None
        
        # Text preprocessor
        self.preprocessor = TextPreprocessor()
        
        # Device configuration
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Model state
        self.is_loaded = False
        
    async def load_model(self):
        """Load ClinicalBERT model and components"""
        try:
            logger.info(f"Loading ClinicalBERT model: {self.model_name}")
            
            # Create cache directory
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                do_lower_case=True
            )
            
            # Load base model for embeddings
            self.base_model = AutoModel.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir
            ).to(self.device)
            
            # Load or create task-specific models
            await self._load_task_models()
            
            # Set models to evaluation mode
            self.base_model.eval()
            if self.readmission_model:
                self.readmission_model.eval()
            if self.ner_model:
                self.ner_model.eval()
                
            self.is_loaded = True
            logger.info("ClinicalBERT model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load ClinicalBERT model: {e}")
            raise
    
    async def _load_task_models(self):
        """Load task-specific model heads"""
        try:
            # Readmission prediction model
            self.readmission_model = ReadmissionPredictor(
                self.base_model.config.hidden_size
            ).to(self.device)
            
            # Try to load pre-trained weights if available
            readmission_weights_path = self.cache_dir / "readmission_model.pth"
            if readmission_weights_path.exists():
                self.readmission_model.load_state_dict(
                    torch.load(readmission_weights_path, map_location=self.device)
                )
                logger.info("Loaded pre-trained readmission model weights")
            else:
                logger.info("Using randomly initialized readmission model")
            
            # Named Entity Recognition model
            try:
                self.ner_model = AutoModelForTokenClassification.from_pretrained(
                    "d4data/biomedical-ner-all",
                    cache_dir=self.cache_dir
                ).to(self.device)
                logger.info("Loaded biomedical NER model")
            except Exception as e:
                logger.warning(f"Could not load NER model: {e}")
                self.ner_model = None
                
        except Exception as e:
            logger.error(f"Error loading task models: {e}")
            raise
    
    async def predict_readmission(
        self, 
        text: str, 
        return_confidence: bool = True
    ) -> Dict[str, Any]:
        """
        Predict 30-day readmission risk
        
        Args:
            text: Clinical note text
            return_confidence: Whether to return confidence scores
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
            
        try:
            # Preprocess text
            processed_text = self.preprocessor.preprocess_clinical_text(text)
            
            # Tokenize
            inputs = self.tokenizer(
                processed_text,
                return_tensors="pt",
                max_length=self.max_length,
                truncation=True,
                padding=True
            ).to(self.device)
            
            # Get embeddings from base model
            with torch.no_grad():
                outputs = self.base_model(**inputs)
                embeddings = outputs.last_hidden_state
                
                # Use CLS token embedding for classification
                cls_embedding = embeddings[:, 0, :]
                
                # Predict readmission risk
                risk_logits = self.readmission_model(cls_embedding)
                risk_prob = torch.sigmoid(risk_logits).cpu().numpy()[0, 0]
                
            result = {
                "readmission_risk": float(risk_prob),
                "risk_category": self._categorize_risk(risk_prob),
                "processing_time": None
            }
            
            if return_confidence:
                # Calculate confidence based on distance from decision boundary
                confidence = abs(risk_prob - 0.5) * 2
                result["confidence"] = float(confidence)
                
            return result
            
        except Exception as e:
            logger.error(f"Error in readmission prediction: {e}")
            raise
    
    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract clinical entities from text
        
        Args:
            text: Clinical note text
            
        Returns:
            Dictionary with extracted entities
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
            
        try:
            # Preprocess text
            processed_text = self.preprocessor.preprocess_clinical_text(text)
            
            entities = []
            
            # Use NER model if available
            if self.ner_model:
                entities.extend(await self._extract_ner_entities(processed_text))
            
            # Rule-based entity extraction as fallback
            rule_based_entities = self._extract_rule_based_entities(processed_text)
            entities.extend(rule_based_entities)
            
            # Remove duplicates and merge overlapping entities
            entities = self._merge_entities(entities)
            
            return {
                "entities": entities,
                "entity_count": len(entities),
                "processing_time": None
            }
            
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            raise
    
    async def _extract_ner_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using NER model"""
        entities = []
        
        try:
            # Tokenize for NER
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=self.max_length,
                truncation=True,
                padding=True,
                return_offsets_mapping=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.ner_model(**{k: v for k, v in inputs.items() if k != 'offset_mapping'})
                predictions = torch.argmax(outputs.logits, dim=2)
                
            # Convert predictions to entities
            tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
            offset_mapping = inputs['offset_mapping'][0]
            
            current_entity = None
            
            for i, (token, pred_id, offset) in enumerate(zip(tokens, predictions[0], offset_mapping)):
                if token in ['[CLS]', '[SEP]', '[PAD]']:
                    continue
                    
                label = self.ner_model.config.id2label.get(pred_id.item(), 'O')
                
                if label.startswith('B-'):
                    # Beginning of new entity
                    if current_entity:
                        entities.append(current_entity)
                    
                    current_entity = {
                        'text': token.replace('##', ''),
                        'label': label[2:],
                        'start': offset[0].item(),
                        'end': offset[1].item(),
                        'confidence': torch.softmax(outputs.logits[0, i], dim=0).max().item()
                    }
                    
                elif label.startswith('I-') and current_entity and label[2:] == current_entity['label']:
                    # Continuation of current entity
                    current_entity['text'] += token.replace('##', '')
                    current_entity['end'] = offset[1].item()
                    
                else:
                    # End of current entity
                    if current_entity:
                        entities.append(current_entity)
                        current_entity = None
            
            # Add final entity if exists
            if current_entity:
                entities.append(current_entity)
                
        except Exception as e:
            logger.error(f"Error in NER extraction: {e}")
            
        return entities
    
    def _extract_rule_based_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using rule-based patterns"""
        entities = []
        
        # Medical patterns
        patterns = {
            'MEDICATION': [
                r'\b(?:mg|mcg|g|ml|units?)\b',
                r'\b\w+(?:cillin|mycin|pril|sartan|statin)\b',
                r'\b(?:aspirin|metformin|insulin|warfarin|heparin)\b'
            ],
            'CONDITION': [
                r'\b(?:diabetes|hypertension|pneumonia|sepsis|MI|CHF)\b',
                r'\b(?:acute|chronic)\s+\w+',
                r'\b\w+(?:itis|osis|pathy|trophy)\b'
            ],
            'PROCEDURE': [
                r'\b(?:surgery|operation|procedure|biopsy|catheter)\b',
                r'\b(?:CT|MRI|X-ray|ultrasound|EKG|ECG)\b',
                r'\b\w+(?:ectomy|otomy|plasty|scopy)\b'
            ],
            'LAB_VALUE': [
                r'\b(?:WBC|RBC|Hgb|Hct|PLT)\s*:?\s*\d+\.?\d*',
                r'\b(?:glucose|creatinine|BUN|sodium|potassium)\s*:?\s*\d+\.?\d*',
                r'\b\d+\.?\d*\s*(?:mg/dL|mmol/L|mEq/L)\b'
            ]
        }
        
        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        'text': match.group(),
                        'label': entity_type,
                        'start': match.start(),
                        'end': match.end(),
                        'confidence': 0.8  # Rule-based confidence
                    })
        
        return entities
    
    def _merge_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge overlapping entities"""
        if not entities:
            return entities
            
        # Sort by start position
        entities.sort(key=lambda x: x['start'])
        
        merged = []
        current = entities[0]
        
        for next_entity in entities[1:]:
            # Check for overlap
            if next_entity['start'] <= current['end']:
                # Merge entities - keep the one with higher confidence
                if next_entity['confidence'] > current['confidence']:
                    current = next_entity
                # Extend end position
                current['end'] = max(current['end'], next_entity['end'])
            else:
                merged.append(current)
                current = next_entity
                
        merged.append(current)
        return merged
    
    async def get_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Get ClinicalBERT embeddings for text(s)
        
        Args:
            texts: Single text or list of texts
            
        Returns:
            Numpy array of embeddings
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
            
        if isinstance(texts, str):
            texts = [texts]
            
        embeddings = []
        
        try:
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]
                
                # Preprocess texts
                processed_texts = [
                    self.preprocessor.preprocess_clinical_text(text) 
                    for text in batch_texts
                ]
                
                # Tokenize
                inputs = self.tokenizer(
                    processed_texts,
                    return_tensors="pt",
                    max_length=self.max_length,
                    truncation=True,
                    padding=True
                ).to(self.device)
                
                # Get embeddings
                with torch.no_grad():
                    outputs = self.base_model(**inputs)
                    # Use mean pooling of all tokens
                    batch_embeddings = outputs.last_hidden_state.mean(dim=1)
                    embeddings.append(batch_embeddings.cpu().numpy())
                    
            return np.vstack(embeddings)
            
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            raise
    
    async def similarity_search(
        self, 
        query_text: str, 
        candidate_texts: List[str],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find similar texts using ClinicalBERT embeddings
        
        Args:
            query_text: Query text
            candidate_texts: List of candidate texts
            top_k: Number of top results to return
            
        Returns:
            List of similar texts with scores
        """
        try:
            # Get embeddings
            query_embedding = await self.get_embeddings(query_text)
            candidate_embeddings = await self.get_embeddings(candidate_texts)
            
            # Calculate cosine similarity
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            candidate_norms = candidate_embeddings / np.linalg.norm(
                candidate_embeddings, axis=1, keepdims=True
            )
            
            similarities = np.dot(candidate_norms, query_norm.T).flatten()
            
            # Get top-k results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                results.append({
                    'text': candidate_texts[idx],
                    'similarity_score': float(similarities[idx]),
                    'index': int(idx)
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk score into levels"""
        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.7:
            return "medium"
        else:
            return "high"
    
    def cleanup(self):
        """Cleanup model resources"""
        if hasattr(self, 'base_model') and self.base_model:
            del self.base_model
        if hasattr(self, 'readmission_model') and self.readmission_model:
            del self.readmission_model
        if hasattr(self, 'ner_model') and self.ner_model:
            del self.ner_model
            
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info("Model resources cleaned up")

class ReadmissionPredictor(nn.Module):
    """Neural network head for readmission prediction"""
    
    def __init__(self, hidden_size: int, dropout_rate: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout_rate)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, 1)
        )
    
    def forward(self, embeddings):
        embeddings = self.dropout(embeddings)
        return self.classifier(embeddings)
