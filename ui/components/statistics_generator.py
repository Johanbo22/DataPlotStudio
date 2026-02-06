import traceback
import pandas as pd
from pathlib import Path
from core.resource_loader import get_resource_path

class StatisticsGenerator:
    """
    Generates HTML statistics reports for DataFrames for the statistics tab
    """
    
    def generate_html(self, df: pd.DataFrame, info: dict) -> str:
        """
        Generates a complete HTML report based on the given dataframe and information
        
        Args:
            df (pd.DataFrame): The dataframe to analyze
            info (dict): Metadata and statistics about the dataframe
            
        Returns:
            str: The formatted HTML string
        """
        try:
            css_content, html_template = self._load_templates()
        except Exception as LoadHTMLError:
            error_msg = f"Failed t load CSS/HTML templates: {str(LoadHTMLError)}"
            traceback.print_exc()
            return f"<p style='color: red;'>{error_msg}</p>"
    
        body_html = ""
        
        # Dataset Overview
        body_html += self._generate_overview_section(df, info)
        
        # Column information
        body_html += self._generate_column_info_section(info)
        
        # Numeric statistics
        body_html += self._generate_numeric_statistics(df)
        
        # Correlation matrix
        body_html += self._generate_correlation_matrix(df)
        
        # Categorical statistics
        body_html += self._generate_categorical_statistics(df)
        
        return html_template.format(
            css_content=css_content, body_content=body_html
        )
    
    def _load_templates(self) -> tuple[str, str]:
        """Loads CSS and HTML templates from resources"""
        css_file_path = Path(get_resource_path("resources/statistics_style.css"))
        html_path = Path(get_resource_path("resources/template.html"))
        
        if not css_file_path.exists():
            raise FileNotFoundError(f"Missing CSS resource file: {css_file_path.resolve()}")
        
        if not html_path.exists():
            raise FileNotFoundError(f"Missing HTML resource file: {html_path.resolve()}")
        
        css_content = css_file_path.read_text(encoding="UTF-8")
        html_template = html_path.read_text(encoding="UTF-8")
        
        return css_content, html_template
    
    def _generate_overview_section(self, df: pd.DataFrame, info: dict) -> str:
        """Generates the general overview section of the statistics"""
        html = "<h2>Dataset Overview</h2>"
        html += "<div class='info-box'>"
        html += f"<div class='info-item'><span class='info-label'>Total Rows:</span> <span class='info-value'>{info.get('shape', [0])[0]:,}</span></div>"
        html += f"<div class='info-item'><span class='info-label'>Total Columns:</span> <span class='info-value'>{len(info.get('columns', []))}</span></div>"
        
        # Memory usage information
        try:
            total_memory_bytes = df.memory_usage(deep=True).sum()
            total_memory = total_memory_bytes / 1024
            if total_memory > 1024:
                memory_str = f"{total_memory / 1024:.2f} MB"
            else:
                memory_str = f"{total_memory:.2f} KB"
        except Exception:
            memory_str = "N/A"
        
        html += f"<div class='info-item'><span class='info-label'>Memory Usage:</span> <span class='info-value'>{memory_str}</span></div>"
        
        try:
            total_missing = sum(info.get("missing_values", {}).values())
        except Exception:
            total_missing = 0
        
        html += f"<div class='info-item'><span class='info-label'>Total Missing Values:</span> <span class='info-value'>{total_missing:,}</span></div>"
        html += "</div>"
        return html
    
    def _generate_column_info_section(self, info: dict) -> str:
        """Generates the information table of the columns"""
        html = "<h2>Column Information</h2>"
        html += "<table>"
        html += "<tr><th>Column Name</th><th>Data Type</th><th>Non-Null Count</th><th>Missing Values</th><th>Missing %</th></tr>"
        
        total_rows = info.get("shape", [0])[0]
        total_missing_check = 0
        
        for col in info.get("columns", []):
            try:
                dtype = str(info.get("dtypes", {}).get(col, "Unknown"))
                missing = info.get("missing_values", {}).get(col, 0)
                total_missing_check += missing
                non_null = total_rows - missing
                missing_pct = (missing / total_rows * 100) if total_rows > 0 else 0
                
                row_class = ""
                if missing_pct > 50:
                    row_class = "style='background-color: #ffebee;'"
                elif missing_pct > 20:
                    row_class = "style='background-color: #fff9c4;'"
                
                html += f"<tr {row_class}>"
                html += f"<td><strong>{col}</strong></td>"
                html += f"<td>{dtype}</td>"
                html += f"<td class='numeric-col'>{non_null:,}</td>"
                html += f"<td class='numeric-col'>{missing:,}</td>"
                html += f"<td class='numeric-col'>{missing_pct:.1f}%</td>"
                html += "</tr>"
            except Exception:
                continue
        
        html += "</table>"
        
        # Warning for missing values
        if total_missing_check > 0:
            high_missing_cols = [col for col, missing in info.get("missing_values", {}).items() if missing > 0]
            
            if high_missing_cols:
                html += "<div class='warning'>"
                html += f"<strong>Warning:</strong> {len(high_missing_cols)} column(s) contain missing values. "
                html += "Consider using data cleaning operations."
                html += "</div>"
        
        return html
    
    def _generate_numeric_statistics(self, df: pd.DataFrame) -> str:
        """Generates the descriptive statistics for numerical columns"""
        html = ""
        try:
            numeric_df = df.select_dtypes(include=["int64", "int32", "float64", "float32"])
            
            if len(numeric_df.columns) > 0:
                html += "<h2>Descriptive Statistics (Numeric Columns)</h2>"
                df_describe = numeric_df.describe()
                
                html += "<table>"
                html += "<tr><th>Statistics</th>"
                for col in df_describe.columns:
                    html += f"<th>{col}</th>"
                html += "</tr>"

                stats_labels = {
                    "count": "Count", "mean": "Mean", "std": "Standard Deviation",
                    "min": "Minimum", "25%": "25th Percentile", "50%": "Median",
                    "75%": "75th Percentile", "max": "Maximum",
                }

                for stat in df_describe.index:
                    html += f"<tr><td><strong>{stats_labels.get(stat, stat)}</strong></td>"
                    for col in df_describe.columns:
                        value = df_describe.loc[stat, col]
                        if stat == "count":
                            html += f"<td class='numeric-col'>{int(value):,}</td>"
                        else:
                            html += f"<td class='numeric-col'>{value:.4f}</td>"
                    html += "</tr>"

                html += "</table>"
        except Exception as UpdateNumericalStatisticsError:
            html += f"<div class='warning'>Unable to calculate numeric statistics: {str(UpdateNumericalStatisticsError)}</div>"
        
        return html
    
    def _generate_correlation_matrix(self, df: pd.DataFrame) -> str:
        """Generates the correlation matrix table"""
        html = ""
        try:
            numeric_df = df.select_dtypes(include=["int64", "int32", "float64", "float32"])

            if len(numeric_df.columns) > 1:
                html += "<h2>Correlation Matrix</h2>"
                corr = numeric_df.corr()

                html += "<table>"
                html += "<tr><th></th>"
                for col in corr.columns:
                    html += f"<th>{col}</th>"
                html += "</tr>"

                for idx in corr.index:
                    html += f"<tr><td><strong>{idx}</strong></td>"
                    for col in corr.columns:
                        value = corr.loc[idx, col]
                        
                        # Color coding
                        cell_style = ""
                        if abs(value) >= 0.8 and idx != col:
                            cell_style = "background-color: #c8e6c9; font-weight: bold;"
                        elif abs(value) >= 0.5 and idx != col:
                            cell_style = "background-color: #fff9c4;"
                        elif idx == col:
                            cell_style = "background-color: #e3f2fd;"

                        html += f"<td class='numeric-col' style='{cell_style}'>{value:.3f}</td>"
                    html += "</tr>"

                html += "</table>"
                
                html += "<div class='info-box'>"
                html += "<strong>Legend:</strong> "
                html += "<span style='background-color: #c8e6c9; padding: 2px 6px; border-radius: 3px;'>Strong correlation (≥0.8)</span> "
                html += "<span style='background-color: #fff9c4; padding: 2px 6px; border-radius: 3px;'>Moderate correlation (≥0.5)</span>"
                html += "</div>"
        except Exception as UpdateCorrelationMatrixError:
            html += f"<div class='warning'>Unable to calculate correlation matrix: {str(UpdateCorrelationMatrixError)}</div>"
            
        return html
    
    def _generate_categorical_statistics(self, df: pd.DataFrame) -> str:
        """Generates statistics for categorical columns."""
        html = ""
        try:
            categorical_df = df.select_dtypes(include=["object", "category"])

            if len(categorical_df.columns) > 0:
                html += "<h2>Categorical Column Statistics</h2>"
                html += "<table>"
                html += "<tr><th>Column</th><th>Unique Values</th><th>Most Common</th><th>Frequency</th></tr>"

                for col in categorical_df.columns:
                    try:
                        unique_count = df[col].nunique()
                        value_counts = df[col].value_counts()

                        if len(value_counts) > 0:
                            most_common = str(value_counts.index[0])
                            most_common_freq = value_counts.iloc[0]

                            html += "<tr>"
                            html += f"<td><strong>{col}</strong></td>"
                            html += f"<td class='numeric-col'>{unique_count}</td>"
                            html += f"<td>{most_common}</td>"
                            html += f"<td class='numeric-col'>{most_common_freq:,}</td>"
                            html += "</tr>"
                    except Exception:
                        continue

                html += "</table>"
        except Exception as UpdateCategoricalStatisticsError:
            html += f"<div class='warning'>Unable to calculate categorical statistics: {str(UpdateCategoricalStatisticsError)}</div>"
            
        return html