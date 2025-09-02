"""Model service for managing ClinicalBERT operations"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import time
import logging
from datetime import datetime

from app.models.clinical_bert import ClinicalBERTModel
from app.services.fhir_adapter import FHIRAdapter
from app.schemas.fhir_schemas import TextInput, FHIRInput, PredictionResponse, EntityExtractionResponse

logger = logging.getLogger(__name__)

class ModelService:
    """Service for managing ClinicalBERT model operations"""
    
    def __init__(self, model: ClinicalBERTModel):
        self.model = model
        self.fhir_adapter = FHIRAdapter()
        
    async def predict_readmission(
        self,
        input_data: Union[TextInput, FHIRInput],
        return_fhir: bool = True
    ) -> PredictionResponse:
        """
        Predict readmission risk from clinical text or FHIR resource
        
        Args:
            input_data: Input text or FHIR resource
            return_fhir: Whether to return FHIR-compliant response
            
        Returns:
            Prediction response
        """
        start_time = time.time()
        
        try:
            # Extract text and metadata
            if isinstance(input_data, FHIRInput):
                text, metadata = self.fhir_adapter.extract_text_from_fhir(input_data.resource)
            else:
                text = input_data.text
                metadata = {
                    'patient_id': input_data.patient_id,
                    'encounter_id': input_data.encounter_id
                }
            
            if not text.strip():
                raise ValueError("No clinical text found in input")
            
            # Get prediction
            prediction_result = await self.model.predict_readmission(text)
            
            processing_time = time.time() - start_time
            
            # Create response
            response = PredictionResponse(
                prediction=prediction_result['readmission_risk'],
                confidence=prediction_result.get('confidence'),
                processing_time=processing_time
            )
            
            # Add FHIR resource if requested
            if return_fhir:
                fhir_observation = self.fhir_adapter.create_observation_resource(
                    prediction_value=prediction_result['readmission_risk'],
                    patient_id=metadata.get('patient_id'),
                    encounter_id=metadata.get('encounter_id'),
                    observation_type="readmission-risk"
                )
                response.fhir_resource = fhir_observation
            
            return response
            
        except Exception as e:
            logger.error(f"Error in readmission prediction: {e}")
            raise
    
    async def extract_entities(
        self,
        input_data: Union[TextInput, FHIRInput],
        return_fhir: bool = True
    ) -> EntityExtractionResponse:
        """
        Extract clinical entities from text or FHIR resource
        
        Args:
            input_data: Input text or FHIR resource
            return_fhir: Whether to return FHIR-compliant response
            
        Returns:
            Entity extraction response
        """
        start_time = time.time()
        
        try:
            # Extract text and metadata
            if isinstance(input_data, FHIRInput):
                text, metadata = self.fhir_adapter.extract_text_from_fhir(input_data.resource)
            else:
                text = input_data.text
                metadata = {
                    'patient_id': input_data.patient_id,
                    'encounter_id': input_data.encounter_id
                }
            
            if not text.strip():
                raise ValueError("No clinical text found in input")
            
            # Extract entities
            extraction_result = await self.model.extract_entities(text)
            
            processing_time = time.time() - start_time
            
            # Create response
            response = EntityExtractionResponse(
                entities=extraction_result['entities'],
                processing_time=processing_time
            )
            
            # Add FHIR resources if requested
            if return_fhir:
                fhir_resources = []
                
                for entity in extraction_result['entities']:
                    if entity['label'] in ['CONDITION', 'DIAGNOSIS']:
                        fhir_condition = self.fhir_adapter.create_condition_resource(
                            condition_text=entity['text'],
                            patient_id=metadata.get('patient_id'),
                            encounter_id=metadata.get('encounter_id')
                        )
                        fhir_resources.append(fhir_condition)
                
                response.fhir_resources = fhir_resources
            
            return response
            
        except Exception as e:
            logger.error(f"Error in entity extraction: {e}")
            raise
    
    async def similarity_search(
        self,
        query_text: str,
        candidate_texts: List[str],
        top_k: int = 10,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search using ClinicalBERT embeddings
        
        Args:
            query_text: Query text
            candidate_texts: List of candidate texts
            top_k: Number of top results
            threshold: Similarity threshold
            
        Returns:
            List of similar texts with scores
        """
        try:
            results = await self.model.similarity_search(
                query_text=query_text,
                candidate_texts=candidate_texts,
                top_k=top_k
            )
            
            # Filter by threshold
            filtered_results = [
                result for result in results 
                if result['similarity_score'] >= threshold
            ]
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    async def get_risk_trajectory(
        self,
        texts: List[str],
        timestamps: Optional[List[datetime]] = None
    ) -> Dict[str, Any]:
        """
        Calculate risk trajectory over multiple clinical notes
        
        Args:
            texts: List of clinical texts in chronological order
            timestamps: Optional timestamps for each text
            
        Returns:
            Risk trajectory data
        """
        try:
            trajectory = []
            
            for i, text in enumerate(texts):
                prediction_result = await self.model.predict_readmission(text)
                
                trajectory_point = {
                    'index': i,
                    'risk_score': prediction_result['readmission_risk'],
                    'risk_category': prediction_result['risk_category'],
                    'confidence': prediction_result.get('confidence', 0.0)
                }
                
                if timestamps and i < len(timestamps):
                    trajectory_point['timestamp'] = timestamps[i].isoformat()
                
                trajectory.append(trajectory_point)
            
            # Calculate trend
            if len(trajectory) > 1:
                risk_scores = [point['risk_score'] for point in trajectory]
                trend = 'increasing' if risk_scores[-1] > risk_scores[0] else 'decreasing'
                if abs(risk_scores[-1] - risk_scores[0]) < 0.1:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            return {
                'trajectory': trajectory,
                'trend': trend,
                'current_risk': trajectory[-1]['risk_score'] if trajectory else 0.0,
                'max_risk': max(point['risk_score'] for point in trajectory) if trajectory else 0.0,
                'min_risk': min(point['risk_score'] for point in trajectory) if trajectory else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk trajectory: {e}")
            raise
    
    async def batch_process(
        self,
        texts: List[str],
        operation: str = "readmission_prediction"
    ) -> List[Dict[str, Any]]:
        """
        Process multiple texts in batch
        
        Args:
            texts: List of texts to process
            operation: Type of operation to perform
            
        Returns:
            List of results
        """
        try:
            results = []
            
            # Process in batches to manage memory
            batch_size = self.model.batch_size
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_results = []
                
                if operation == "readmission_prediction":
                    for text in batch_texts:
                        result = await self.model.predict_readmission(text)
                        batch_results.append(result)
                        
                elif operation == "entity_extraction":
                    for text in batch_texts:
                        result = await self.model.extract_entities(text)
                        batch_results.append(result)
                        
                elif operation == "embeddings":
                    embeddings = await self.model.get_embeddings(batch_texts)
                    for j, embedding in enumerate(embeddings):
                        batch_results.append({
                            'text_index': i + j,
                            'embedding': embedding.tolist()
                        })
                
                results.extend(batch_results)
                
                # Small delay to prevent overwhelming the system
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            raise
