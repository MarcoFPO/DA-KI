"""
Analysis service for handling stock analysis operations.
"""
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from src.database.db_access import DBAccess
from src.models.api_models import AnalysisRequest, AnalysisResult, TechnicalScore, EventScore

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service class for stock analysis operations."""
    
    def __init__(self, db_access: DBAccess):
        """
        Initialize AnalysisService with database access.
        
        Args:
            db_access: Database access layer instance
        """
        self.db_access = db_access
        # Initialize analysis engines (lazy loading)
        self._scoring_engine = None
        self._event_scoring_engine = None
        self._ml_predictor = None
        self._data_preparation = None
    
    @property
    def scoring_engine(self):
        """Lazy load scoring engine."""
        if self._scoring_engine is None:
            from src.backend_components.scoring_engine import ScoringEngine
            self._scoring_engine = ScoringEngine()
        return self._scoring_engine
    
    @property
    def event_scoring_engine(self):
        """Lazy load event scoring engine."""
        if self._event_scoring_engine is None:
            from src.backend_components.event_scoring_engine import EventScoringEngine
            self._event_scoring_engine = EventScoringEngine()
        return self._event_scoring_engine
    
    @property
    def ml_predictor(self):
        """Lazy load ML predictor."""
        if self._ml_predictor is None:
            from src.backend_components.ml_predictor import MLPredictor
            self._ml_predictor = MLPredictor()
        return self._ml_predictor
    
    @property
    def data_preparation(self):
        """Lazy load data preparation."""
        if self._data_preparation is None:
            from src.backend_components.data_preparation import DataPreparation
            self._data_preparation = DataPreparation()
        return self._data_preparation
    
    async def analyze_stocks(self, analysis_request: AnalysisRequest, user_id: int) -> List[AnalysisResult]:
        """
        Perform comprehensive analysis on list of tickers.
        
        Args:
            analysis_request: Analysis request with tickers
            user_id: User ID for logging and auditing
            
        Returns:
            List of AnalysisResult objects
        """
        results = []
        
        logger.info(f"Starting analysis for {len(analysis_request.tickers)} tickers for user {user_id}")
        
        for ticker in analysis_request.tickers:
            try:
                result = await self._analyze_single_stock(ticker, user_id)
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error analyzing ticker {ticker} for user {user_id}: {str(e)}")
                results.append(AnalysisResult(
                    ticker=ticker,
                    status="failed",
                    message=f"Analysis failed: {str(e)}",
                    timestamp=datetime.utcnow()
                ))
        
        logger.info(f"Completed analysis for user {user_id}: {len(results)} results generated")
        return results
    
    async def _analyze_single_stock(self, ticker: str, user_id: int) -> AnalysisResult:
        """
        Perform analysis on a single stock.
        
        Args:
            ticker: Stock ticker symbol
            user_id: User ID for logging
            
        Returns:
            AnalysisResult object
        """
        logger.debug(f"Analyzing ticker {ticker} for user {user_id}")
        
        # Get historical data
        historical_data = await self.db_access.get_historical_data_for_ticker(ticker)
        if not historical_data:
            return AnalysisResult(
                ticker=ticker,
                status="failed",
                message="No historical data available",
                timestamp=datetime.utcnow()
            )
        
        # Perform technical analysis
        technical_score = await self._perform_technical_analysis(ticker, historical_data)
        
        # Perform event-driven analysis
        event_score = await self._perform_event_analysis(ticker)
        
        # Perform ML prediction
        ml_prediction, ml_confidence = await self._perform_ml_prediction(ticker, historical_data)
        
        return AnalysisResult(
            ticker=ticker,
            status="success",
            message="Analysis completed successfully",
            technical_score=technical_score,
            event_score=event_score,
            ml_prediction=ml_prediction,
            ml_confidence=ml_confidence,
            timestamp=datetime.utcnow()
        )
    
    async def _perform_technical_analysis(self, ticker: str, historical_data: List[Dict]) -> Optional[TechnicalScore]:
        """
        Perform technical analysis using scoring engine.
        
        Args:
            ticker: Stock ticker symbol
            historical_data: Historical price and indicator data
            
        Returns:
            TechnicalScore object or None if analysis fails
        """
        try:
            score_output = await self.scoring_engine.calculate_total_score(ticker, historical_data)
            
            return TechnicalScore(
                total_score=score_output.get("total_score", 0.0),
                individual_scores=score_output.get("individual_scores", {}),
                confidence_level=score_output.get("confidence_level", "low"),
                recommendation=score_output.get("recommendation", "hold"),
                signal_strength=score_output.get("signal_strength", "weak")
            )
            
        except Exception as e:
            logger.error(f"Technical analysis failed for {ticker}: {str(e)}")
            return None
    
    async def _perform_event_analysis(self, ticker: str) -> Optional[EventScore]:
        """
        Perform event-driven analysis.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            EventScore object or None if analysis fails
        """
        try:
            # Get event data from database (placeholder implementation)
            event_data = await self.db_access.get_event_data_for_ticker(ticker)
            
            if not event_data:
                # Return default/empty event score
                return EventScore(
                    total_event_score=0.0,
                    individual_events={},
                    weighted_events={},
                    active_events=[]
                )
            
            score_output = await self.event_scoring_engine.calculate_event_score(event_data)
            
            return EventScore(
                total_event_score=score_output.get("total_event_score", 0.0),
                individual_events=score_output.get("individual_events", {}),
                weighted_events=score_output.get("weighted_events", {}),
                active_events=score_output.get("active_events", [])
            )
            
        except Exception as e:
            logger.error(f"Event analysis failed for {ticker}: {str(e)}")
            return None
    
    async def _perform_ml_prediction(self, ticker: str, historical_data: List[Dict]) -> tuple[Optional[float], Optional[float]]:
        """
        Perform ML-based prediction.
        
        Args:
            ticker: Stock ticker symbol
            historical_data: Historical price and indicator data
            
        Returns:
            Tuple of (prediction, confidence) or (None, None) if prediction fails
        """
        try:
            # Prepare data for ML
            prepared_data = await self.data_preparation.prepare_data_for_ml(ticker, historical_data)
            
            if prepared_data.empty:
                logger.warning(f"Not enough data for ML prediction for {ticker}")
                return None, None
            
            # Get ML prediction
            prediction = await self.ml_predictor.predict(ticker, prepared_data.to_dict(orient='records'))
            
            # Calculate confidence (placeholder implementation)
            confidence = 0.75  # TODO: Implement actual confidence calculation
            
            return prediction, confidence
            
        except Exception as e:
            logger.error(f"ML prediction failed for {ticker}: {str(e)}")
            return None, None
    
    async def get_analysis_history(self, user_id: int, limit: int = 100) -> List[AnalysisResult]:
        """
        Get analysis history for user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results to return
            
        Returns:
            List of historical AnalysisResult objects
        """
        try:
            # TODO: Implement analysis history storage and retrieval
            logger.info(f"Getting analysis history for user {user_id} (limit: {limit})")
            return []
            
        except Exception as e:
            logger.error(f"Error getting analysis history for user {user_id}: {str(e)}")
            raise