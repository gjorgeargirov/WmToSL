import json
import os
from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime

class MigrationEstimator:
    """Class to estimate migration time based on file size and historical data"""
    
    def __init__(self, history_file: str = "migration_history.json"):
        self.history_file = history_file
        self.size_time_data = self._load_size_time_data()
        
    def _load_size_time_data(self) -> List[Dict]:
        """Load historical size-time data from file"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as file:
                data = json.load(file)
                # Convert string data to proper format if needed
                if isinstance(data, list) and data and isinstance(data[0], str):
                    # If data is just a list of project names, try to load detailed history
                    detailed_file = f"{self.history_file}.detailed"
                    if os.path.exists(detailed_file):
                        with open(detailed_file, 'r') as f:
                            return json.load(f)
                    return []
                return data
        return []
    
    def _save_size_time_data(self, data: List[Dict]) -> None:
        """Save size-time data to file"""
        with open(f"{self.history_file}.detailed", 'w') as file:
            json.dump(data, file, indent=2)
    
    def add_migration_record(self, project_name: str, file_size_mb: float, duration_seconds: float) -> None:
        """Add a new migration record to the history"""
        record = {
            "project_name": project_name,
            "file_size_mb": file_size_mb,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.now().isoformat()
        }
        
        self.size_time_data.append(record)
        self._save_size_time_data(self.size_time_data)
    
    def estimate_migration_time(self, file_size_mb: float) -> Tuple[float, Dict]:
        """
        Estimate migration time based on file size and historical data
        
        Returns:
            Tuple containing:
            - Estimated time in seconds
            - Dictionary with estimation details
        """
        # Base processing time (in seconds) for any migration, regardless of size
        BASE_PROCESSING_TIME = 60  # 1 minute minimum processing time
        
        # Calculate complexity factor based on file size
        if file_size_mb < 0.1:  # Very small files (< 100KB)
            complexity_factor = 1
        elif file_size_mb < 1:  # Small files (< 1MB)
            complexity_factor = 1.5
        elif file_size_mb < 10:  # Medium files (< 10MB)
            complexity_factor = 2
        else:  # Large files (>= 10MB)
            complexity_factor = 2.5
        
        if not self.size_time_data:
            # If no historical data, use size-based estimate
            estimated_time = BASE_PROCESSING_TIME * complexity_factor
            if file_size_mb > 0:
                estimated_time += (file_size_mb * 30)  # Add 30 seconds per MB
            
            return estimated_time, {
                "method": "size_based_estimate",
                "confidence": "medium",
                "sample_size": 0,
                "explanation": f"Based on file size of {file_size_mb:.2f} MB. "
                             f"Larger files typically take longer to process due to more content to analyze and migrate.",
                "complexity": "low" if file_size_mb < 1 else "medium" if file_size_mb < 10 else "high"
            }
        
        # Extract size and time data
        sizes = np.array([record["file_size_mb"] for record in self.size_time_data])
        times = np.array([record["duration_seconds"] for record in self.size_time_data])
        
        # Find similar size records for better estimation
        similar_size_records = [
            record for record in self.size_time_data 
            if 0.5 * file_size_mb <= record["file_size_mb"] <= 1.5 * file_size_mb
        ]
        
        if similar_size_records and len(similar_size_records) >= 3:
            # Use median of similar-sized files
            similar_times = [record["duration_seconds"] for record in similar_size_records]
            estimated_time = np.median(similar_times) * complexity_factor
            
            return estimated_time, {
                "method": "historical_data",
                "confidence": "high",
                "sample_size": len(similar_size_records),
                "explanation": f"Based on {len(similar_size_records)} similar migrations. "
                             f"Files of size {file_size_mb:.2f} MB typically take {self.format_time_estimate(np.median(similar_times))} to migrate.",
                "complexity": "low" if file_size_mb < 1 else "medium" if file_size_mb < 10 else "high",
                "similar_sizes_range": f"{min(sizes):.2f} MB - {max(sizes):.2f} MB"
            }
        else:
            # Use linear regression if we have enough data
            if len(self.size_time_data) >= 5:
                slope, intercept = np.polyfit(sizes, times, 1)
                estimated_time = (slope * file_size_mb + intercept) * complexity_factor
                
                return estimated_time, {
                    "method": "regression_estimate",
                    "confidence": "medium",
                    "sample_size": len(self.size_time_data),
                    "explanation": f"Based on analysis of {len(self.size_time_data)} previous migrations. "
                                 f"Estimated using file size of {file_size_mb:.2f} MB and historical migration patterns.",
                    "complexity": "low" if file_size_mb < 1 else "medium" if file_size_mb < 10 else "high",
                    "data_range": f"{min(sizes):.2f} MB - {max(sizes):.2f} MB"
                }
            
            # Fallback to size-based estimate with historical context
            estimated_time = BASE_PROCESSING_TIME * complexity_factor
            if file_size_mb > 0:
                estimated_time += (file_size_mb * 30)  # Add 30 seconds per MB
            
            return estimated_time, {
                "method": "size_based_estimate",
                "confidence": "low",
                "sample_size": len(self.size_time_data),
                "explanation": f"Limited data for files of size {file_size_mb:.2f} MB. "
                             f"Estimate based on file size and general processing patterns.",
                "complexity": "low" if file_size_mb < 1 else "medium" if file_size_mb < 10 else "high",
                "note": "This is a conservative estimate. Actual migration time may vary."
            }
    
    def get_migration_statistics(self) -> Dict:
        """Get statistics about past migrations"""
        if not self.size_time_data:
            return {
                "total_migrations": 0,
                "average_time": 0,
                "average_size": 0
            }
        
        times = [record["duration_seconds"] for record in self.size_time_data]
        sizes = [record["file_size_mb"] for record in self.size_time_data]
        
        return {
            "total_migrations": len(self.size_time_data),
            "average_time": np.mean(times),
            "average_size": np.mean(sizes),
            "median_time": np.median(times),
            "median_size": np.median(sizes),
            "min_time": min(times),
            "max_time": max(times),
            "min_size": min(sizes),
            "max_size": max(sizes)
        }
    
    def format_time_estimate(self, seconds: float) -> str:
        """Format time estimate in a human-readable format with explanation"""
        if seconds < 60:
            return f"{seconds:.0f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} hours" 