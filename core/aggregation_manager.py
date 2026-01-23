from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import pandas as pd

@dataclass
class SavedAggregation:
    """Represents a saved aggregation config and result"""
    name: str
    description: str
    group_by: List[str]
    agg_config: Dict[str, str]
    date_grouping: Optional[Dict[str, str]] = None
    result_df: Optional[pd.DataFrame] = None
    created_at: datetime = field(default_factory=datetime.now)
    row_count: int = 0
    
    agg_columns: List[str] = field(default_factory=list)
    agg_func: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return {
            "name": self.name,
            "description": self.description,
            "group_by": self.group_by,
            "agg_config": self.agg_config,
            "date_grouping": self.date_grouping,
            "agg_columns": list(self.agg_config.keys()) if self.agg_config else [],
            "agg_func": "mixed",
            "created_at": self.created_at.isoformat(),
            "row_count": self.row_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SavedAggregation":
        """Create from dict"""
        created_at = datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
        
        agg_config = data.get("agg_config")
        if not agg_config:
            cols = data.get("agg_columns", [])
            func = data.get("agg_func", "count")
            agg_config = {col: func for col in cols}

        return cls(
            name=data["name"],
            description=data.get("description", ""),
            group_by=data["group_by"],
            agg_config=agg_config,
            date_grouping=data.get("date_grouping"),
            created_at=created_at,
            row_count=data.get("row_count", 0)
        )

class AggregationManager:
    """Manages saved aggregation"""

    def __init__(self):
        self.saved_aggregations: Dict[str, SavedAggregation] = {}
    
    def save_aggregation(self, name: str, description: str, group_by: List[str], agg_config: Dict[str, str], result_df: pd.DataFrame, date_grouping: Dict[str, str] = None) -> SavedAggregation:
        """Save an aggregation"""
        if name in self.saved_aggregations:
            raise ValueError(f"Aggregation '{name}' already exists")
        
        agg = SavedAggregation(
            name=name,
            description=description,
            group_by=group_by,
            agg_config=agg_config,
            date_grouping=date_grouping,
            result_df=result_df.copy(),
            row_count=len(result_df)
        )

        self.saved_aggregations[name] = agg
        return agg
    
    def get_aggregation(self, name: str) -> Optional[SavedAggregation]:
        """Get a saved aggregation"""
        return self.saved_aggregations.get(name)
    
    def list_aggregations(self) -> List[str]:
        """List he saved aggregation by name"""
        return list(self.saved_aggregations.keys())
    
    def delete_aggregation(self, name: str) -> bool:
        """Delete a saved aggregation from the list"""
        if name in self.saved_aggregations:
            del self.saved_aggregations[name]
            return True
        return False
    
    def get_aggregation_df(self, name: str) -> Optional[pd.DataFrame]:
        """Get the dataframe result of a saved aggregation"""
        agg = self.saved_aggregations.get(name)
        return agg.result_df.copy() if agg and agg.result_df is not None else None
    
    def reapply_aggregation(self, name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Reapply an agg to a new dataframe"""
        agg = self.saved_aggregations.get(name)

        if not agg:
            raise ValueError(f"Aggregation '{name}' not found")
        
        agg_dict = {col: (col, agg.agg_func) for col in agg.agg_columns}
        result = df.groupby(agg.group_by).agg(**agg_dict).reset_index()

        agg.result_df = result.copy()
        agg.row_count = len(result)

        return result
    
    def export_aggregation(self) -> Dict[str, Any]:
        """Export aggregations for project saving"""
        return {
            name: agg.to_dict() for name, agg in self.saved_aggregations.items()
        }
    
    def import_aggregations(self, data: Dict[str, Any]) -> None:
        """"Import aggregations from another project"""
        self.saved_aggregations.clear()
        for name, agg_data in data.items():
            self.saved_aggregations[name] = SavedAggregation.from_dict(agg_data)
    
    def clear_all(self) -> None:
        """Clear all saved aggregations"""
        self.saved_aggregations.clear()