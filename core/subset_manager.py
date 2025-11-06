#core/subset_manager
"""Class to handle subsets of data"""
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Subset:
    """A Named subset of data with filtering criteria"""
    name: str
    description: str
    filters: List[Dict[str, Any]]
    logic: str = "AND"
    created_at: datetime = field(default_factory=datetime.now)
    row_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert subset to dict for saving"""
        return {
            "name": self.name,
            "description": self.description,
            "filters": self.filters,
            "logic": self.logic,
            "created_at": self.created_at,
            "row_count": self.row_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Subset":
        """Create a subset from dict"""
        created_at = datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
        return cls(
            name=data["name"],
            description=data["description"],
            filters=data["filters"],
            logic=data.get("logic", "AND"),
            created_at=created_at,
            row_count=data.get("row_count", 0)
        )

class SubsetManager:
    """Creates, stores and uses data subsets"""

    def __init__(self):
        self.subsets: Dict[str, Subset] = {}
        self._cached_data: Dict[str, pd.DataFrame] = {}
    
    def create_subset(self, name: str, description: str, filters: List[Dict[str, Any]], logic: str = "AND") -> Subset:
        """Create a new subset definition"""
        if name in self.subsets:
            raise ValueError(f"Subset '{name}' already exists")
        
        subset = Subset(
            name=name,
            description=description,
            filters=filters,
            logic=logic
        )
        
        self.subsets[name] = subset
        return subset
    
    def update_subset(self, name: str, description: Optional[str] = None, filters: Optional[List[Dict[str, Any]]] = None, logic: Optional[str] = None) -> Subset:
        """Update existing subset"""
        if name not in self.subsets:
            raise ValueError(f"Subset '{name} does not exists'")
        
        subset = self.subsets[name]
        if description is not None:
            subset.description = description
        if filters is not None:
            subset.filters = filters
        if logic is not None:
            subset.logic = logic
        
        #invalidate cache
        if name in self._cached_data:
            del self._cached_data[name]
        
        return subset
    
    def delete_subset(self, name: str) -> bool:
        """Delete a subset"""
        if name in self.subsets:
            del self.subsets[name]
            if name in self._cached_data:
                del self._cached_data[name]
            return True
        return False
    
    def get_subset(self, name: str) -> Optional[Subset]:
        """Get subset definition"""
        return self.subsets.get(name)
    
    def list_subsets(self) -> List[str]:
        """List all subsets"""
        return list(self.subsets.keys())
    
    def apply_subset(self, df: pd.DataFrame, name: str, use_cache: bool = True) -> pd.DataFrame:
        """Apply subset filters to dataframe and return the filtered data"""
        if name not in self.subsets:
            raise ValueError(f"Subset '{name}' does not exists")
        
        #check cache
        if use_cache and name in self._cached_data:
            return self._cached_data[name].copy()
        
        subset = self.subsets[name]
        filtered_df = self._apply_filters(df, subset.filters, subset.logic)

        #update row count
        subset.row_count = len(filtered_df)

        #cache the result
        if use_cache:
            self._cached_data[name] = filtered_df.copy()

        return filtered_df
    
    def _apply_filters(self, df: pd.DataFrame, filters: List[Dict[str, Any]], logic: str) -> pd.DataFrame:
        """APpply all filters"""
        if not filters:
            return df.copy()
        
        if logic == "AND":
            # apply filters in sequence
            result = df.copy()
            for f in filters:
                result = self._apply_single_filter(result, f)
            return result
        
        else: #hanlde or logic
            mask = pd.Series([False] * len(df))
            for f in filters:
                filtered = self._apply_single_filter(df, f)
                mask = mask | df.index.isin(filtered.index)
            return df[mask]
    
    def _apply_single_filter(self, df: pd.DataFrame, filter_def: Dict[str, Any]) -> pd.DataFrame:
        """Apply a singulear filter to df"""
        column = filter_def["column"]
        condition = filter_def["condition"]
        value = filter_def["value"]

        # type conversion
        if column in df.columns:
            col_dtype = df[column].dtype
            try:
                if pd.api.types.is_integer_dtype(col_dtype):
                    value = int(value)
                elif pd.api.types.is_float_dtype(col_dtype):
                    value = float(value)
            except (ValueError, TypeError):
                pass
        
        # apply cons
        if condition == ">":
            return df[df[column] > value]
        elif condition == "<":
            return df[df[column] < value]
        elif condition == "==":
            return df[df[column] == value]
        elif condition == "!=":
            return df[df[column] != value]
        elif condition == ">=":
            return df[df[column] >= value]
        elif condition == "<=":
            return df[df[column] <= value]
        elif condition == "contains":
            return df[df[column].astype(str).str.contains(str(value), na=False)]
        elif condition == "in":
            if not isinstance(value, (list, tuple, set)):
                value = [value]
            return df[df[column].isin(value)]
        else:
            raise ValueError(f"Unknown condition: {condition}")
    
    def clear_cache(self, name: Optional[str] = None) -> None:
        """Clear cached subset data"""
        if name:
            if name in self._cached_data:
                del self._cached_data
        else:
            self._cached_data.clear()
    
    def get_subset_info(self, name: str) -> Dict[str, Any]:
        """Get info about a subset"""
        if name not in self.subsets:
            raise ValueError(f"Subset '{name}' does not exist")
        
        subset = self.subsets[name]
        return {
            "name": subset.name,
            "description": subset.description,
            "filters": subset.filters,
            "logic": subset.logic,
            "created_at": subset.created_at,
            "row_count": subset.row_count,
            "is_cached": name in self._cached_data
        }
    
    def export_subsets(self) -> Dict[str, Any]:
        """Export all subsets"""
        return {
            name: subset.to_dict()
            for name, subset in self.subsets.items()
        }

    def import_subsets(self, data: Dict[str, Any]):
        """Import subsets"""
        self.subsets.clear()
        self._cached_data.clear()

        for name, subset_data in data.items():
            self.subsets[name] = Subset.from_dict(subset_data)

    def create_subset_from_unique_values(self, df: pd.DataFrame, column: str, prefix: str = "") -> List[str]:
        """
        Create multiple subsets based on unique values in a column.
        useful for splitting data by more columns such as location, category etc.

        Returns a list of created subset names
        """
        if column not in df.columns:
            raise ValueError(f"Column: {column} not found in DataFrame")
        
        unique_values = df[column].unique()
        created_subsets = []

        for value in unique_values:
            #create a safe name fot the subset
            subset_name = f"{prefix}{column}_{value}".replace(" ", "_")

            #skip if the subset already exists
            if subset_name in self.subsets:
                continue

            #create filter
            filters = [{
                "column": column,
                "condition": "==",
                "value": value
            }]

            #create the subset
            try:
                self.create_subset(
                    name=subset_name,
                    description=f"Auto Created subset: {column} = {value}",
                    filters=filters,
                    logic="AND"
                )
                created_subsets.append(subset_name)
            except ValueError:
                continue
        
        return created_subsets