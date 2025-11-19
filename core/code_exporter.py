# core/code_exporter.py
from typing import Dict, Any, List, Set
from datetime import datetime
from pathlib import Path
import re
from arrow import get
import pandas as pd

class CodeExporter:
    """
    Generates a complete, runnable Python script by inspecting
    the final UI state of the DataHandler and PlotTab.
    """
    
    def __init__(self):
        self.imports: Set[str] = set()
        self.script_lines: List[str] = []

    def _add_imports(self, plot_config: Dict[str, Any]):
        """Dynamically add required imports based on UI config."""
        self.imports.clear()
        self.imports.add("import pandas as pd")
        self.imports.add("import numpy as np")
        self.imports.add("import matplotlib.pyplot as plt")
        self.imports.add("import seaborn as sns")
        self.imports.add("import requests")
        self.imports.add("from io import StringIO")
        self.imports.add("import traceback")
        self.imports.add("from sqlalchemy import create_engine")
        self.imports.add("from sqlalchemy.sql import text")
        
        plot_type = plot_config.get("plot_type")
        
        if plot_config.get("axes", {}).get("datetime", {}).get("enabled"):
            self.imports.add("import matplotlib.dates as mdates")
        
        if plot_config.get("axes", {}).get("x_axis", {}).get("max_ticks", 10) < 30 or \
        plot_config.get("axes", {}).get("y_axis", {}).get("max_ticks", 10) < 30:
            self.imports.add("from matplotlib.ticker import MaxNLocator")
        
        scatter_analysis = plot_config.get("advanced", {}).get("scatter", {})
        if scatter_analysis.get("show_regression") or \
        scatter_analysis.get("show_ci") or \
        scatter_analysis.get("show_r2") or \
        scatter_analysis.get("show_rmse") or \
        scatter_analysis.get("show_equation") or \
        scatter_analysis.get("error_bars", "None") != "None":
            self.imports.add("from scipy import stats")
            if scatter_analysis.get("show_ci"):
                self.imports.add("from scipy.stats import t as t_dist")

        hist_analysis = plot_config.get("advanced", {}).get("histogram", {})
        if hist_analysis.get("show_normal"):
            self.imports.add("from scipy.stats import norm")
        if hist_analysis.get("show_kde") or plot_type == "KDE":
            self.imports.add("from scipy.stats import gaussian_kde")

    def _clean_value(self, value: Any) -> str:
        """Helper to format values for insertion into code."""
        if isinstance(value, str):
            # Escape single quotes and backslashes
            cleaned = value.replace("\\", "\\\\").replace("'", "\\'")
            return f"'{cleaned}'"
        if value is None:
            return "None"
        # Handle dicts for line/bar customizations
        if isinstance(value, dict):
            items = []
            for k, v in value.items():
                items.append(f"{self._clean_value(k)}: {self._clean_value(v)}")
            return "{" + ", ".join(items) + "}"
        return str(value)

    def _generate_header(self) -> str:
        """Generates the script header and imports."""
        header = [
            f"\"\"\"",
            "DataPlot Studio - Generated Analysis Script",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "This script replicates the data loading, processing, and",
            "visualization steps performed in DataPlot Studio.",
            "\"\"\"",
            "",
        ]
        header.extend(sorted(list(self.imports)))
        return "\n".join(header)

    def _generate_data_loader(self, data_filepath: str, source_info: Dict[str, Any]) -> str:
        """Generates the data loading section."""
        lines = ["", "def load_data():", "    \"\"\"Load data from source.\"\"\""]
        
        if source_info.get("last_db_connection_string") and source_info.get("last_db_query"):
            conn_string = self._clean_value(source_info.get("last_db_connection_string"))
            query = self._clean_value(source_info.get("last_db_query"))
            
            lines.append("    print('Loading data from Database...')")
            lines.append(f"    connection_string = {conn_string}")
            lines.append(f"    query = text({query})")
            lines.append("    try:")
            lines.append("        engine = create_engine(connection_string)")
            lines.append("        with engine.connect() as connection:")
            lines.append("            df = pd.read_sql_query(query, connection)")
            lines.append("        print('Data loaded successfully from database.')")
            lines.append("        return df")
            lines.append("    except ImportError as e:")
            lines.append("        print('Error: Missing database driver. Please install, e.g., pip install psycopg2-binary')")
            lines.append("        return None")
            lines.append("    except Exception as e:")
            lines.append("        print(f'Failed to load from database: {{e}}')")
            lines.append("        print('Please check connection string (password may be missing), query, and drivers.')")
            lines.append("        return None")

        elif source_info.get("is_temp_file"):
            # It's a Google Sheet import
            sheet_id = self._clean_value(source_info.get("last_gsheet_id"))
            sheet_name = self._clean_value(source_info.get("last_gsheet_name"))
            delimiter = self._clean_value(source_info.get("last_gsheet_delimiter", ","))
            decimal = self._clean_value(source_info.get("last_gsheet_decimal", "."))
            thousands = self._clean_value(source_info.get("last_gsheet_thousands"))

            lines.append("    print('Loading data from Google Sheets...')")
            lines.append(f"    sheet_id = {sheet_id}")
            lines.append(f"    sheet_name = {sheet_name}")
            lines.append(f"    url = f'https://docs.google.com/spreadsheets/d/{{sheet_id}}/gviz/tq?tqx=out:csv&sheet={{sheet_name}}'")
            lines.append("    try:")
            lines.append("        response = requests.get(url, timeout=10)")
            lines.append("        response.raise_for_status()")
            lines.append(f"        df = pd.read_csv(StringIO(response.text), sep={delimiter}, decimal={decimal}, thousands={thousands}, engine='python', on_bad_lines='skip')")
            lines.append("        print('Data loaded successfully.')")
            lines.append("        return df")
            lines.append("    except Exception as e:")
            lines.append("        print(f'Failed to load Google Sheet: {{e}}')")
            lines.append("        return None")
            
        else:
            # It's a local file import
            filepath_str = f"r'{data_filepath}'".replace("\\", "\\\\")
            lines.append(f"    filepath = {filepath_str}")
            lines.append("    print(f'Loading data from {{filepath}}...')")
            ext = Path(data_filepath).suffix.lower()
            lines.append("    try:")
            if ext in ['.xlsx', '.xls']:
                lines.append("        df = pd.read_excel(filepath)")
            elif ext == '.json':
                lines.append("        df = pd.read_json(filepath)")
            elif ext == '.txt':
                lines.append("        df = pd.read_csv(filepath, sep='\\t')")
            else: # Default to CSV
                lines.append("        df = pd.read_csv(filepath)")
            lines.append("        print('Data loaded successfully.')")
            lines.append("        return df")
            lines.append("    except Exception as e:")
            lines.append("        print(f'Failed to load local file: {{e}}')")
            lines.append("        return None")
            
        lines.append("\n")
        return "\n".join(lines)

    def _generate_data_ops(self, data_operations: List[Dict[str, Any]]) -> str:
        """Generates the data processing function."""
        lines = ["", "def process_data(df):", "    \"\"\"Apply data operations.\"\"\""]
        if not data_operations:
            lines.append("    print('No data operations to apply.')")
            lines.append("    return df")
            return "\n".join(lines)
            
        lines.append("    print('Applying data operations...')")
        lines.append("    df_processed = df.copy()")
        
        for i, op in enumerate(data_operations):
            op_type = op.get("type")
            lines.append(f"\n    # Operation {i+1}: {op_type}")
            
            try:
                if op_type == "filter":
                    col = self._clean_value(op['column'])
                    cond = op['condition']
                    val = op['value'] # Get raw value
                    
                    # Try to auto-convert numeric, but fall back to string
                    val_str = self._clean_value(val)
                    lines.append("    try:")
                    lines.append(f"        # Attempt numeric conversion for filter value")
                    lines.append(f"        filter_val = {val_str}")
                    lines.append("        if isinstance(filter_val, (int, float)):")
                    lines.append(f"            df_processed[{col}] = pd.to_numeric(df_processed[{col}], errors='coerce')")
                    lines.append("    except Exception:")
                    lines.append(f"        filter_val = {val_str}")

                    if cond == "contains":
                        lines.append(f"    df_processed = df_processed[df_processed[{col}].astype(str).str.contains(str(filter_val), na=False)]")
                    elif cond == "in":
                        # Value for 'in' should be a list
                        val_list = [val] if not isinstance(val, (list, tuple, set)) else val
                        lines.append(f"    df_processed = df_processed[df_processed[{col}].isin({self._clean_value(val_list)})]")
                    else:
                        lines.append(f"    df_processed = df_processed[df_processed[{col}] {cond} filter_val]")
                
                elif op_type == "drop_duplicates":
                    lines.append("    df_processed = df_processed.drop_duplicates()")
                
                elif op_type == "drop_missing":
                    lines.append("    df_processed = df_processed.dropna()")
                
                elif op_type == "fill_missing":
                    method = self._clean_value(op.get('method', 'ffill'))
                    lines.append(f"    df_processed = df_processed.fillna(method={method})")
                
                elif op_type == "drop_column":
                    col = self._clean_value(op['column'])
                    lines.append(f"    df_processed = df_processed.drop(columns=[{col}])")
                
                elif op_type == "rename_column":
                    old = self._clean_value(op['old_name'])
                    new = self._clean_value(op['new_name'])
                    lines.append(f"    df_processed = df_processed.rename(columns={{{old}: {new}}})")
                
                elif op_type == "change_data_type":
                    col = self._clean_value(op['column'])
                    new_type = op['new_type']
                    if new_type == "string":
                        lines.append(f"    df_processed[{col}] = df_processed[{col}].astype(pd.StringDtype())")
                    elif new_type == "int":
                        lines.append(f"    df_processed[{col}] = pd.to_numeric(df_processed[{col}], errors='coerce').astype(pd.Int64Dtype())")
                    elif new_type == "float":
                        lines.append(f"    df_processed[{col}] = pd.to_numeric(df_processed[{col}], errors='coerce').astype(pd.Float64Dtype())")
                    elif new_type == "category":
                        lines.append(f"    df_processed[{col}] = df_processed[{col}].astype('category')")
                    elif new_type == "datetime":
                        lines.append(f"    df_processed[{col}] = pd.to_datetime(df_processed[{col}], errors='coerce', utc=True)")
                
                elif op_type == "aggregate":
                    group_by = op['group_by']
                    agg_cols = op['agg_columns']
                    agg_func = op['agg_func']
                    agg_dict = ", ".join([f"{self._clean_value(c)}: ({self._clean_value(c)}, {self._clean_value(agg_func)})" for c in agg_cols])
                    lines.append(f"    df_processed = df_processed.groupby({group_by}).agg({agg_dict}).reset_index()")
            
            except Exception as e:
                lines.append(f"    # FAILED TO PARSE OPERATION: {op} -> {e}")
        
        lines.append("\n    print('Data operations applied.')")
        lines.append("    return df_processed")
        return "\n".join(lines)

    def _generate_scatter_analysis(self, get_cfg, x_col, y_col_str, flip_axes) -> List[str]:
        """Helper to generate scatter plot analysis code."""
        lines = []
        scatter_cfg = get_cfg("advanced.scatter", {})
        if not (scatter_cfg.get("show_regression") or scatter_cfg.get("show_ci") or scatter_cfg.get("show_r2") or
                scatter_cfg.get("show_rmse") or scatter_cfg.get("show_equation") or
                scatter_cfg.get("error_bars", "None") != "None"):
            return lines

        lines.append("\n    # --- Scatter Plot Analysis ---")
        lines.append("    try:")
        lines.append("        # Prepare data for analysis (drop NaNs)")
        lines.append(f"        analysis_df = df[[{x_col}, {y_col_str}]].dropna().copy()")
        lines.append(f"        x_data_raw = analysis_df[{x_col}].values")
        lines.append(f"        y_data_raw = analysis_df[{y_col_str}].values")
        lines.append("        if len(x_data_raw) < 2:")
        lines.append("            print('Not enough data for regression analysis.')")
        lines.append("        else:")
        lines.append("            slope, intercept, r_value, p_value, std_err = stats.linregress(x_data_raw, y_data_raw)")
        lines.append("            x_line = np.linspace(x_data_raw.min(), x_data_raw.max(), 100)")
        lines.append("            y_line = slope * x_line + intercept")
        
        if scatter_cfg.get("show_regression"):
            lines.append("            # Plot regression line (styling applied globally later)")
            # Draw a basic line matching plot_tab.py's default before customization
            lines.append(f"            ax.plot({ 'y_line, x_line' if flip_axes else 'x_line, y_line'}, color='red', ls='-', lw=2, label='Linear Fit', gid='regression_line')")
        
        if scatter_cfg.get("show_ci"):
            lines.append("            # Calculate and plot confidence interval")
            lines.append(f"            confidence = {scatter_cfg.get('ci_level', 95) / 100.0}")
            lines.append("            n = len(x_data_raw)")
            lines.append("            residuals = y_data_raw - (slope * x_data_raw + intercept)")
            lines.append("            residual_std = np.sqrt(np.sum(residuals**2) / (n - 2))")
            lines.append("            x_mean = np.mean(x_data_raw)")
            lines.append("            se_line = residual_std * np.sqrt(1/n + (x_line - x_mean)**2 / np.sum((x_data_raw - x_mean)**2))")
            lines.append("            t_val = t_dist.ppf((1 + confidence) / 2, n - 2)")
            lines.append("            margin = t_val * se_line")
            if flip_axes:
                lines.append("            ax.fill_betweenx(x_line, y_line - margin, y_line + margin, color='red', alpha=0.15, label=f'{int(confidence*100)}% CI', gid='confidence_interval')")
            else:
                lines.append("            ax.fill_between(x_line, y_line - margin, y_line + margin, color='red', alpha=0.15, label=f'{int(confidence*100)}% CI', gid='confidence_interval')")

        lines.append("            # Prepare stats text")
        lines.append("            stats_text = []")
        lines.append(f"            eq_x, eq_y = ('y', 'x') if {flip_axes} else ('x', 'y')")
        if scatter_cfg.get("show_equation"):
            lines.append("            op = '+' if intercept >= 0 else '-'")
            # --- FIX: Removed extra {{}} ---
            lines.append("            stats_text.append(f'{eq_y} = {slope:.4f}{eq_x} {op} {abs(intercept):.4f}')")
        if scatter_cfg.get("show_r2"):
            lines.append("            stats_text.append(f'R² = {r_value**2:.4f}')")
        if scatter_cfg.get("show_rmse"):
            lines.append("            y_pred = slope * x_data_raw + intercept")
            lines.append("            rmse = np.sqrt(np.mean((y_data_raw - y_pred)**2))")
            lines.append("            stats_text.append(f'RMSE = {rmse:.4f}')")
        # --- END FIX ---
        
        lines.append("            if stats_text:")
        lines.append("                textstr = '\\n'.join(stats_text)")
        lines.append("                props = dict(boxstyle='round', facecolor='wheat', alpha=0.85)")
        lines.append(f"                ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=11, verticalalignment='top', bbox=props, fontfamily={self._clean_value(get_cfg('appearance.font_family', 'Arial'))})")

        error_bar_type = scatter_cfg.get("error_bars", "None")
        if error_bar_type == "Standard Deviation":
            lines.append("            # (Standard Deviation error bar export is complex, skipping for now)") # Per-bin logic
        # --- FIX: Implemented Standard Error ---
        elif error_bar_type == "Standard Error":
            lines.append("            # Add Standard Error bars")
            lines.append("            y_pred_all = slope * x_data_raw + intercept")
            lines.append("            residuals = y_data_raw - y_pred_all")
            lines.append(f"            residual_std = np.sqrt(np.sum(residuals**2) / (len(x_data_raw) - 2))")
            lines.append("            x_mean = np.mean(x_data_raw)")
            lines.append("            se_points = residual_std * np.sqrt(1/len(x_data_raw) + (x_data_raw - x_mean)**2 / np.sum((x_data_raw - x_mean)**2))")
            lines.append("            step = max(1, len(x_data_raw) // 30)")
            lines.append("            err_args = (x_data_raw[::step], y_data_raw[::step])")
            lines.append(f"            err_kwargs = {{'yerr': se_points[::step]}} if not {flip_axes} else {{'xerr': se_points[::step]}}")
            lines.append("            ax.errorbar(*err_args, **err_kwargs, fmt='o', ecolor='gray', markersize=3, alpha=0.5, capsize=4, zorder=8, markerfacecolor='none', markeredgecolor='none', elinewidth=1, linestyle='none')")
        # --- END FIX ---

        lines.append("    except Exception as e:")
        lines.append("        print(f'Failed to add scatter analysis: {{e}}')")
        lines.append("        traceback.print_exc()")
        
        return lines

    def _generate_plot_code(self, df: pd.DataFrame, plot_config: Dict[str, Any]) -> str:
        """Generates the plotting function."""
        lines = ["", "def create_plot(df):", "    \"\"\"Create the visualization.\"\"\""]
        
        # Helper function to safely get nested dict keys
        def get_cfg(path, default=None):
            keys = path.split('.')
            val = plot_config
            try:
                for key in keys:
                    val = val[key]
                return val
            except (KeyError, TypeError):
                return default

        # --- 1. Set up Figure and Style ---
        lines.append("\n    # --- 1. Set up Figure and Style ---")
        style = self._clean_value(get_cfg("appearance.figure.style", "default"))
        lines.append(f"    plt.style.use({style})")
        lines.append(f"    fig, ax = plt.subplots(")
        lines.append(f"        figsize=({get_cfg('appearance.figure.width', 10)}, {get_cfg('appearance.figure.height', 6)}),")
        lines.append(f"        dpi={get_cfg('appearance.figure.dpi', 100)}")
        lines.append("    )")
        lines.append(f"    fig.set_facecolor({self._clean_value(get_cfg('appearance.figure.bg_color', 'white'))})")
        lines.append(f"    ax.set_facecolor({self._clean_value(get_cfg('appearance.figure.face_color', 'white'))})")
        lines.append(f"    font_family = {self._clean_value(get_cfg('appearance.font_family', 'Arial'))}")
        lines.append("    plt.rcParams['font.family'] = font_family")
        
        # --- 2. Data and Plot Type ---
        lines.append("\n    # --- 2. Data and Plot Type ---")
        plot_type = get_cfg("plot_type", "Scatter")
        x_col_raw = get_cfg("basic.x_column")
        x_col = self._clean_value(x_col_raw)
        y_cols_raw = get_cfg("basic.y_columns", [])
        y_col_raw = y_cols_raw[0] if y_cols_raw else None
        y_col_str = self._clean_value(y_col_raw)
        y_cols_str = self._clean_value(y_cols_raw)
        hue_raw = get_cfg("basic.hue_column", "None")
        hue = hue_raw if hue_raw != "None" else None
        hue_str = self._clean_value(hue)
        palette = self._clean_value(get_cfg("appearance.figure.palette", "deep"))
        alpha = get_cfg("advanced.global_alpha", 1.0)
        flip_axes = get_cfg("axes.flip_axes", False)
        
        # Convert datetime columns if they exist
        lines.append("    # Convert datetime columns for plotting")
        lines.append("    try:")
        if x_col_raw and x_col_raw in df.columns and "datetime" in str(df.dtypes.get(x_col_raw, '')):
            lines.append(f"        df[{x_col}] = pd.to_datetime(df[{x_col}], errors='coerce', utc=True)")
        else:
            lines.append("        pass")
        for y_c in y_cols_raw:
            if y_c in df.columns and "datetime" in str(df.dtypes.get(y_c, '')):
                lines.append(f"        df[{self._clean_value(y_c)}] = pd.to_datetime(df[{self._clean_value(y_c)}], errors='coerce', utc=True)")
        lines.append("    except Exception as e:")
        lines.append("        print(f'Warning: Could not convert datetime columns: {{e}}')")

        # Subset Warning
        if get_cfg("basic.use_subset"):
            subset_name = self._clean_value(get_cfg("basic.subset_name"))
            lines.append("    # WARNING: This plot uses a subset. The export tool cannot replicate subset logic.")
            lines.append("    # The plot will be generated on the full (processed) data.")
            lines.append(f"    print(f'WARNING: Plot was originally for subset {subset_name}, running on full data.')")
        
        # --- 3. Generate Plot ---
        lines.append("\n    # --- 3. Generate Plot ---")
        lines.append(f"    plot_type = {self._clean_value(plot_type)}")
        
        # Global plot kwargs from UI
        g_plot_kwargs = f"data=df, palette={palette}, hue={hue_str}, ax=ax"
        g_adv_kwargs = f"alpha={alpha}"
        g_line_kwargs = get_cfg("advanced.global_line", {})
        g_marker_kwargs = get_cfg("advanced.global_marker", {})
        g_bar_kwargs = get_cfg("advanced.global_bar", {})
        
        # Handle flipped axes
        x_plot, y_plot = (x_col, y_col_str)
        orient = "'v'"
        if flip_axes:
            x_plot, y_plot = (y_col_str, x_col)
            orient = "'h'"

        if plot_type == "Line":
            lines.append("    # Matplotlib ax.plot mimics plot_engine.py")
            lines.append(f"    g_marker_shape_raw = {self._clean_value(g_marker_kwargs.get('shape', 'None'))}")
            lines.append(f"    g_marker_shape = g_marker_shape_raw if g_marker_shape_raw != 'None' else None")
            lines.append("    plot_args = {")
            lines.append(f"        'marker': g_marker_shape,")
            lines.append(f"        'markersize': {g_marker_kwargs.get('size', 6)},")
            lines.append(f"        'linestyle': {self._clean_value(g_line_kwargs.get('style', '-'))},")
            lines.append(f"        'linewidth': {g_line_kwargs.get('width', 1.5)},")
            lines.append(f"        'alpha': {alpha}")
            lines.append("    }")
            lines.append(f"    if {hue_str}:")
            lines.append(f"        for group in df[{hue_str}].unique():")
            lines.append(f"            mask = df[{hue_str}] == group")
            lines.append(f"            for y_col in {y_cols_str}:")
            lines.append(f"                ax.plot(df.loc[mask, {x_col}], df.loc[mask, y_col], label=f'{{y_col}} - {{group}}', **plot_args)")
            lines.append("    else:")
            lines.append(f"        for y_col in {y_cols_str}:")
            lines.append(f"            ax.plot(df[{x_col}], df[y_col], label=y_col, **plot_args)")

        elif plot_type == "Scatter":
            lines.append("    # Matplotlib ax.scatter mimics plot_engine.py")
            # --- FIX: Let ax.scatter use its default marker ('o') if UI is "None" ---
            lines.append(f"    g_marker_shape_raw = {self._clean_value(g_marker_kwargs.get('shape', 'o'))}")
            lines.append(f"    g_marker_shape = g_marker_shape_raw if g_marker_shape_raw != 'None' else 'o'")
            lines.append("    plot_args = {")
            lines.append(f"        's': {g_marker_kwargs.get('size', 6)}**2,") # scatter uses 's'
            lines.append(f"        'marker': g_marker_shape,")
            lines.append(f"        'alpha': {alpha},")
            lines.append(f"        'edgecolors': None if {self._clean_value(g_marker_kwargs.get('edge_color'))} == 'Auto' else {self._clean_value(g_marker_kwargs.get('edge_color'))},")
            lines.append(f"        'linewidths': {g_marker_kwargs.get('edge_width', 1.0)},")
            lines.append(f"        'c': None if {self._clean_value(g_marker_kwargs.get('color'))} == 'Auto' else {self._clean_value(g_marker_kwargs.get('color'))}")
            lines.append("    }")
            lines.append(f"    if {hue_str}:")
            lines.append(f"        # Use seaborn for scatter with hue, as it's much simpler")
            lines.append(f"        sns.scatterplot({g_plot_kwargs}, x={x_plot}, y={y_plot}, {g_adv_kwargs}, marker=g_marker_shape, s={g_marker_kwargs.get('size', 6)**2})")
            lines.append("    else:")
            lines.append("        # Use matplotlib for simple scatter")
            lines.append(f"        ax.scatter(df[{x_plot}], df[{y_plot}], label={y_col_str}, **plot_args)")

        elif plot_type == "Bar":
            lines.append("    # Bar plot logic mimicking plot_engine.py")
            lines.append(f"    g_bar_width = {g_bar_kwargs.get('width', 0.8)}")
            lines.append(f"    if {hue_str} and len({y_cols_str}) == 1:")
            lines.append("        # Single Y with Hue (uses seaborn)")
            lines.append(f"        sns.barplot({g_plot_kwargs}, x={x_plot}, y={y_plot}, orient={orient}, {g_adv_kwargs}, width=g_bar_width)")
            lines.append(f"    elif len({y_cols_str}) > 1:")
            lines.append("        # Grouped bar chart (matplotlib)")
            lines.append(f"        x_labels = df[{x_col}].unique()")
            lines.append("        x_pos = np.arange(len(x_labels))")
            lines.append(f"        num_y = len({y_cols_str})")
            lines.append(f"        bar_width = g_bar_width / num_y")
            lines.append(f"        for i, col in enumerate({y_cols_str}):")
            lines.append("            offset = (i - num_y / 2) * bar_width + bar_width / 2")
            lines.append(f"            values = [df[df[{x_col}] == label][col].values[0] if len(df[df[{x_col}] == label]) > 0 else 0 for label in x_labels]")
            lines.append(f"            if {flip_axes}:")
            lines.append("                ax.barh(x_pos + offset, values, height=bar_width, label=col)")
            lines.append("            else:")
            lines.append("                ax.bar(x_pos + offset, values, width=bar_width, label=col)")
            lines.append(f"        if {flip_axes}:")
            lines.append("            ax.set_yticks(x_pos)")
            lines.append("            ax.set_yticklabels(x_labels)")
            lines.append("        else:")
            lines.append("            ax.set_xticks(x_pos)")
            lines.append("            ax.set_xticklabels(x_labels)")
            lines.append("    else:")
            lines.append("        # Single Y, no Hue (matplotlib)")
            lines.append(f"        if {flip_axes}:")
            lines.append(f"            ax.barh(df[{x_col}], df[{y_col_str}], height=g_bar_width, label={y_col_str})")
            lines.append("        else:")
            lines.append(f"            ax.bar(df[{x_col}], df[{y_col_str}], width=g_bar_width, label={y_col_str})")

        elif plot_type == "Histogram":
            hist_cfg = get_cfg("advanced.histogram", {})
            lines.append(f"    data_col = df[{y_col_str}].dropna()")
            lines.append(f"    n, bins, patches = ax.hist(data_col, {g_adv_kwargs}, bins={hist_cfg.get('bins', 30)}, density={hist_cfg.get('show_normal') or hist_cfg.get('show_kde')})")
            if hist_cfg.get("show_normal"):
                lines.append("    # Overlay Normal Distribution")
                lines.append("    try:")
                lines.append("        mu, sigma = data_col.mean(), data_col.std()")
                lines.append("        x_norm = np.linspace(bins[0], bins[-1], 100)")
                lines.append("        y_norm = norm.pdf(x_norm, mu, sigma)")
                lines.append("        # Scale normal curve to histogram")
                lines.append("        bin_width = (data_col.max() - data_col.min()) / " + str(hist_cfg.get('bins', 30)))
                lines.append("        y_norm_scaled = y_norm * len(data_col) * bin_width")
                lines.append("        ax.plot(x_norm, y_norm_scaled, 'r--', linewidth=2.5, label=f'Normal (μ={{mu:.2f}}, σ={{sigma:.2f}})')")
                lines.append("    except Exception as e: print(f'Could not plot normal curve: {{e}}')")
            if hist_cfg.get("show_kde"):
                lines.append("    # Overlay KDE")
                lines.append("    try:")
                lines.append("        kde = gaussian_kde(data_col)")
                lines.append("        x_kde = np.linspace(bins[0], bins[-1], 100)")
                lines.append("        y_kde = kde(x_kde)")
                lines.append("        ax.plot(x_kde, y_kde, 'g-', linewidth=2.5, label='KDE')")
                lines.append("    except Exception as e: print(f'Could not plot KDE curve: {{e}}')")

        elif plot_type == "Box":
            lines.append(f"    # Box plot mimics plot_engine.py (using pandas)")
            lines.append(f"    df.plot(kind='box', column={y_cols_str}, ax=ax, vert={not flip_axes})")
        
        elif plot_type == "Violin":
            lines.append(f"    sns.violinplot({g_plot_kwargs}, x={x_plot}, y={y_plot}, orient={orient}, {g_adv_kwargs})")
        
        elif plot_type == "KDE":
            lines.append(f"    # KDE plot mimics plot_engine.py (using pandas)")
            lines.append(f"    df[{y_col_str}].plot(kind='kde', ax=ax, {g_adv_kwargs})")
        
        elif plot_type == "Area":
            lines.append("    # Stacked Area Plot")
            lines.append("    try:")
            lines.append(f"        df_plot = df.set_index({x_col})[{y_cols_str}]")
            lines.append(f"        df_plot.plot(kind='area', ax=ax, stacked=True, {g_adv_kwargs}, colormap={palette})")
            lines.append("    except Exception as e:")
            lines.append("        print(f'Could not generate area plot: {{e}}')")

        elif plot_type == "Pie":
            pie_cfg = get_cfg("advanced.pie", {})
            lines.append("    # Pie Plot")
            lines.append("    try:")
            lines.append(f"        pie_data = df.groupby({x_col})[{y_col_str}].sum()")
            lines.append("        explode = None")
            if pie_cfg.get("explode_first"):
                lines.append(f"        explode = [0.0] * len(pie_data)")
                lines.append(f"        if explode: explode[0] = {pie_cfg.get('explode_distance', 0.1)}")
            lines.append(f"        ax.pie(pie_data, labels=pie_data.index, autopct={'%1.2f%%' if pie_cfg.get('show_percentages') else None},")
            lines.append(f"               startangle={pie_cfg.get('start_angle', 0)}, shadow={pie_cfg.get('shadow', False)}, explode=explode)")
            lines.append("        ax.set_ylabel('')") # Clear default y-label
            lines.append("    except Exception as e: print(f'Could not generate pie plot: {{e}}')")

        elif plot_type == "Count Plot":
            lines.append(f"    sns.countplot({g_plot_kwargs}, x={x_plot}, y={y_plot}, orient={orient}, {g_adv_kwargs})")
            
        elif plot_type == "Hexbin":
            lines.append("    # Hexbin Plot")
            lines.append("    try:")
            lines.append(f"        ax.hexbin(df[{x_col}], df[{y_col_str}], gridsize=20, {g_adv_kwargs}, cmap={palette})")
            lines.append("    except Exception as e: print(f'Could not generate hexbin plot: {{e}}')")

        elif plot_type == "2D Density":
            lines.append(f"    sns.kdeplot({g_plot_kwargs}, x={x_col}, y={y_col_str}, fill=True, {g_adv_kwargs}, cmap={palette})")

        else:
            lines.append(f"    # Plot type {plot_type} not supported by exporter, using scatter.")
            lines.append(f"    sns.scatterplot({g_plot_kwargs}, x={x_plot}, y={y_plot}, {g_adv_kwargs})")

        # --- 4. Scatter Plot Analysis (if applicable) ---
        lines.append("\n    # --- 4. Scatter Plot Analysis (if applicable) ---")
        if plot_type == "Scatter":
            lines.extend(self._generate_scatter_analysis(get_cfg, x_col, y_col_str, flip_axes))

        # --- 5. Apply Advanced Customizations (Lines and Bars) ---
        lines.append("\n    # --- 5. Apply Advanced Customizations (Lines and Bars) ---")
        lines.append("    # This mimics _apply_plot_customizations from plot_tab.py")
        lines.append(f"    g_line_color = {self._clean_value(g_line_kwargs.get('color'))}")
        lines.append(f"    g_marker_color = {self._clean_value(g_marker_kwargs.get('color'))}")
        lines.append(f"    g_marker_edge_color = {self._clean_value(g_marker_kwargs.get('edge_color'))}")
        lines.append(f"    g_marker_edge_width = {g_marker_kwargs.get('edge_width', 1.0)}")
        lines.append(f"    line_customs = {self._clean_value(get_cfg('advanced.line_customizations', {}))}")
        lines.append("    all_lines = ax.get_lines()")
        lines.append(f"    if {get_cfg('advanced.multi_line_custom', False)}:")
        lines.append("        for line in all_lines:")
        lines.append("            label = line.get_label()")
        lines.append("            if label in line_customs:")
        lines.append("                line.set(**line_customs[label])") # Apply specific customization
        lines.append("    else:") # Apply global customization
        lines.append("        for line in all_lines:")
        lines.append("            if line.get_gid() == 'confidence_interval': continue") # Don't style CI fill
        lines.append(f"            if g_line_color and g_line_color != 'Auto': line.set_color(g_line_color)")
        lines.append(f"            if g_marker_color and g_marker_color != 'Auto': line.set_markerfacecolor(g_marker_color)")
        lines.append(f"            if g_marker_edge_color and g_marker_edge_color != 'Auto': line.set_markeredgecolor(g_marker_edge_color)")
        lines.append(f"            if g_marker_edge_width: line.set_markeredgewidth(g_marker_edge_width)")

        lines.append(f"    g_bar_color = {self._clean_value(g_bar_kwargs.get('color'))}")
        lines.append(f"    g_bar_edgecolor = {self._clean_value(g_bar_kwargs.get('edge_color'))}")
        lines.append(f"    g_bar_edgewidth = {g_bar_kwargs.get('edge_width', 1.0)}")
        lines.append(f"    bar_customs = {self._clean_value(get_cfg('advanced.bar_customizations', {}))}")
        lines.append(f"    if {get_cfg('advanced.multi_bar_custom', False)}:")
        lines.append("        legend_handles, legend_labels = ax.get_legend_handles_labels()")
        lines.append("        for i, container in enumerate(ax.containers):")
        lines.append("            label = None")
        lines.append("            try: label = legend_labels[i]") # Try to get label from legend
        lines.append("            except: label = container.get_label() or f'Bar Series {{i+1}}'")
        lines.append("            if label in bar_customs:")
        lines.append("                plt.setp(container.patches, **bar_customs[label])")
        lines.append(f"    elif {alpha} != 1.0 or g_bar_color or g_bar_edgecolor:") # Apply global
        lines.append("        global_bar_style = {}")
        lines.append(f"        if g_bar_color and g_bar_color != 'Auto': global_bar_style['facecolor'] = g_bar_color")
        lines.append(f"        if g_bar_edgecolor and g_bar_edgecolor != 'Auto': global_bar_style['edgecolor'] = g_bar_edgecolor")
        lines.append(f"        if g_bar_edgewidth: global_bar_style['linewidth'] = g_bar_edgewidth")
        lines.append(f"        global_bar_style['alpha'] = {alpha}")
        lines.append("        plt.setp(ax.patches, **global_bar_style)")


        # --- 6. Customize Appearance (Titles/Labels) ---
        lines.append("\n    # --- 6. Customize Appearance (Titles/Labels) ---")
        xlabel_text_cfg = get_cfg('appearance.xlabel.text')
        xlabel_to_set = xlabel_text_cfg if xlabel_text_cfg else x_col_raw
        ylabel_text_cfg = get_cfg('appearance.ylabel.text')
        ylabel_to_set = ylabel_text_cfg if ylabel_text_cfg else (y_col_raw if len(y_cols_raw)==1 else 'Value')
        
        if get_cfg("appearance.title.enabled", True):
            lines.append(f"    ax.set_title(")
            lines.append(f"        label={self._clean_value(get_cfg('appearance.title.text', plot_type))},")
            lines.append(f"        fontsize={get_cfg('appearance.title.size', 14)},")
            lines.append(f"        fontweight={self._clean_value(get_cfg('appearance.title.weight', 'bold'))},")
            lines.append(f"        fontfamily=font_family")
            lines.append("    )")
        else:
            lines.append("    ax.set_title('')")
            
        if get_cfg("appearance.xlabel.enabled", True):
            lines.append(f"    ax.set_xlabel(")
            lines.append(f"        xlabel={self._clean_value(xlabel_to_set)},")
            lines.append(f"        fontsize={get_cfg('appearance.xlabel.size', 12)},")
            lines.append(f"        fontweight={self._clean_value(get_cfg('appearance.xlabel.weight', 'normal'))},")
            lines.append(f"        fontfamily=font_family")
            lines.append("    )")
        else:
            lines.append("    ax.set_xlabel('')")

        if get_cfg("appearance.ylabel.enabled", True):
            lines.append(f"    ax.set_ylabel(")
            lines.append(f"        ylabel={self._clean_value(ylabel_to_set)},")
            lines.append(f"        fontsize={get_cfg('appearance.ylabel.size', 12)},")
            lines.append(f"        fontweight={self._clean_value(get_cfg('appearance.ylabel.weight', 'normal'))},")
            lines.append(f"        fontfamily=font_family")
            lines.append("    )")
        else:
            lines.append("    ax.set_ylabel('')")
        # --- END FIX ---

        # --- 7. Customize Spines ---
        lines.append("\n    # --- 7. Customize Spines ---")
        for side in ['top', 'bottom', 'left', 'right']:
            lines.append(f"    ax.spines[{self._clean_value(side)}].set_visible({get_cfg(f'appearance.spines.{side}.visible', True)})")
            lines.append(f"    ax.spines[{self._clean_value(side)}].set_linewidth({get_cfg(f'appearance.spines.{side}.width', 1.0)})")
            lines.append(f"    ax.spines[{self._clean_value(side)}].set_color({self._clean_value(get_cfg(f'appearance.spines.{side}.color', 'black'))})")

        # --- 8. Customize Axes (Limits, Ticks, Scale) ---
        lines.append("\n    # --- 8. Customize Axes (Limits, Ticks, Scale) ---")
        if not get_cfg("axes.x_axis.auto_limits", True):
            lines.append(f"    ax.set_xlim({get_cfg('axes.x_axis.min')}, {get_cfg('axes.x_axis.max')})")
        if not get_cfg("axes.y_axis.auto_limits", True):
            lines.append(f"    ax.set_ylim({get_cfg('axes.y_axis.min')}, {get_cfg('axes.y_axis.max')})")
        
        if get_cfg("axes.x_axis.invert", False): lines.append("    ax.invert_xaxis()")
        if get_cfg("axes.y_axis.invert", False): lines.append("    ax.invert_yaxis()")
            
        lines.append(f"    ax.set_xscale({self._clean_value(get_cfg('axes.x_axis.scale', 'linear'))})")
        lines.append(f"    ax.set_yscale({self._clean_value(get_cfg('axes.y_axis.scale', 'linear'))})")
        
        # Ticks
        lines.append(f"    ax.tick_params(axis='x', labelsize={get_cfg('axes.x_axis.tick_label_size')}, rotation={get_cfg('axes.x_axis.tick_rotation')}, " +
                    f"which='major', direction={self._clean_value(get_cfg('axes.x_axis.major_tick_direction'))}, width={get_cfg('axes.x_axis.major_tick_width')})")
        lines.append(f"    ax.tick_params(axis='y', labelsize={get_cfg('axes.y_axis.tick_label_size')}, rotation={get_cfg('axes.y_axis.tick_rotation')}, " +
                    f"which='major', direction={self._clean_value(get_cfg('axes.y_axis.major_tick_direction'))}, width={get_cfg('axes.y_axis.major_tick_width')})")
        if get_cfg("axes.x_axis.minor_ticks_enabled"):
            lines.append("    ax.minorticks_on()")
            lines.append(f"    ax.tick_params(axis='x', which='minor', direction={self._clean_value(get_cfg('axes.x_axis.minor_tick_direction'))}, width={get_cfg('axes.x_axis.minor_tick_width')})")
        if get_cfg("axes.y_axis.minor_ticks_enabled"):
            lines.append("    ax.minorticks_on()")
            lines.append(f"    ax.tick_params(axis='y', which='minor', direction={self._clean_value(get_cfg('axes.y_axis.minor_tick_direction'))}, width={get_cfg('axes.y_axis.minor_tick_width')})")

        lines.append(f"    ax.xaxis.set_major_locator(MaxNLocator(nbins={get_cfg('axes.x_axis.max_ticks', 10)}))")
        lines.append(f"    ax.yaxis.set_major_locator(MaxNLocator(nbins={get_cfg('axes.y_axis.max_ticks', 10)}))")

        # Datetime Formatting
        if get_cfg("axes.datetime.enabled", False):
            lines.append("    # Apply Datetime Formatting")
            x_fmt_preset = get_cfg("axes.datetime.x_format_preset", "Auto")
            x_fmt_custom = get_cfg("axes.datetime.x_format_custom", "")
            x_fmt = x_fmt_custom if x_fmt_preset == "Custom" and x_fmt_custom else (x_fmt_preset.split(" ")[0] if x_fmt_preset != "Auto" else None)
            if x_fmt:
                lines.append(f"    try: ax.xaxis.set_major_formatter(mdates.DateFormatter({self._clean_value(x_fmt)}))")
                lines.append("    except Exception as e: print(f'Failed to set x-axis datetime format: {{e}}')")

            y_fmt_preset = get_cfg("axes.datetime.y_format_preset", "Auto")
            y_fmt_custom = get_cfg("axes.datetime.y_format_custom", "")
            y_fmt = y_fmt_custom if y_fmt_preset == "Custom" and y_fmt_custom else (y_fmt_preset.split(" ")[0] if y_fmt_preset != "Auto" else None)
            if y_fmt:
                lines.append(f"    try: ax.yaxis.set_major_formatter(mdates.DateFormatter({self._clean_value(y_fmt)}))")
                lines.append("    except Exception as e: print(f'Failed to set y-axis datetime format: {{e}}')")


        # --- 9. Customize Grid ---
        lines.append("\n    # --- 9. Customize Grid ---")
        if get_cfg("grid.enabled", False):
            if get_cfg("grid.independent_axes", False):
                cfg = get_cfg("grid.x_major")
                style = cfg['style'][cfg['style'].find('(')+1:cfg['style'].find(')')]
                lines.append(f"    ax.grid({cfg['enabled']}, which='major', axis='x', ls={self._clean_value(style)}, lw={cfg['width']}, color={self._clean_value(cfg['color'])}, alpha={cfg['alpha']})")
                cfg = get_cfg("grid.x_minor")
                style = cfg['style'][cfg['style'].find('(')+1:cfg['style'].find(')')]
                lines.append(f"    ax.grid({cfg['enabled']}, which='minor', axis='x', ls={self._clean_value(style)}, lw={cfg['width']}, color={self._clean_value(cfg['color'])}, alpha={cfg['alpha']})")
                cfg = get_cfg("grid.y_major")
                style = cfg['style'][cfg['style'].find('(')+1:cfg['style'].find(')')]
                lines.append(f"    ax.grid({cfg['enabled']}, which='major', axis='y', ls={self._clean_value(style)}, lw={cfg['width']}, color={self._clean_value(cfg['color'])}, alpha={cfg['alpha']})")
                cfg = get_cfg("grid.y_minor")
                style = cfg['style'][cfg['style'].find('(')+1:cfg['style'].find(')')]
                lines.append(f"    ax.grid({cfg['enabled']}, which='minor', axis='y', ls={self._clean_value(style)}, lw={cfg['width']}, color={self._clean_value(cfg['color'])}, alpha={cfg['alpha']})")
            else:
                cfg = get_cfg("grid.global")
                lines.append(f"    ax.grid(True, which={self._clean_value(cfg['which'])}, axis={self._clean_value(cfg['axis'])}, alpha={cfg['alpha']})")
        else:
            lines.append("    ax.grid(False)")


        # --- 10. Customize Legend ---
        lines.append("\n    # --- 10. Customize Legend ---")
        # --- FIX: Always run legend() if checked, let matplotlib handle empty labels ---
        if get_cfg("legend.enabled", False):
            lines.append("    try:")
            lines.append("        handles, labels = ax.get_legend_handles_labels()")
            lines.append("        if handles or labels:") # Only create legend if there's something to show
            lines.append("            legend = ax.legend(handles=handles, labels=labels,")
            lines.append(f"                loc={self._clean_value(get_cfg('legend.location', 'best'))},")
            lines.append(f"                title={self._clean_value(get_cfg('legend.title'))},")
            lines.append(f"                fontsize={get_cfg('legend.font_size', 10)},")
            lines.append(f"                ncols={get_cfg('legend.columns', 1)},")
            lines.append(f"                columnspacing={get_cfg('legend.column_spacing', 1.0)},")
            lines.append(f"                frameon={get_cfg('legend.frame', True)},")
            lines.append(f"                fancybox={get_cfg('legend.fancy_box', True)},")
            lines.append(f"                shadow={get_cfg('legend.shadow', False)},")
            lines.append(f"                framealpha={get_cfg('legend.alpha', 1.0)},")
            lines.append(f"                facecolor={self._clean_value(get_cfg('legend.bg_color', 'white'))},")
            lines.append(f"                edgecolor={self._clean_value(get_cfg('legend.edge_color', 'black'))}")
            lines.append("            )")
            lines.append("            if legend and legend.get_frame():")
            lines.append(f"                legend.get_frame().set_linewidth({get_cfg('legend.edge_width', 1.0)})")
            lines.append("            if legend and legend.get_title():")
            lines.append(f"                legend.get_title().set_fontfamily(font_family)")
            lines.append("            if legend:")
            lines.append("                for text in legend.get_texts():")
            lines.append(f"                    text.set_fontfamily(font_family)")
            lines.append("    except: pass")
        else:
            lines.append("    if ax.get_legend(): ax.get_legend().remove()")
        

        # --- 11. Add Annotations ---
        lines.append("\n    # --- 11. Add Annotations ---")
        for ann in get_cfg("annotations.text_annotations", []):
            lines.append(f"    ax.text(x={ann['x']}, y={ann['y']}, s={self._clean_value(ann['text'])}, " +
                        f"fontsize={ann['fontsize']}, color={self._clean_value(ann['color'])}, " +
                        "transform=ax.transAxes, ha='center', va='center', " +
                        "bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))")

        if get_cfg("annotations.textbox.enabled", False) and get_cfg("annotations.textbox.content"):
            lines.append("    # Add Textbox")
            tb_cfg = get_cfg("annotations.textbox")
            pos_map = {
                "upper left": (0.05, 0.95, 'left', 'top'), "upper center": (0.5, 0.95, 'center', 'top'), "upper right": (0.95, 0.95, 'right', 'top'),
                "center left": (0.05, 0.5, 'left', 'center'), "center": (0.5, 0.5, 'center', 'center'), "center right": (0.95, 0.5, 'right', 'center'),
                "lower left": (0.05, 0.05, 'left', 'bottom'), "lower center": (0.5, 0.05, 'center', 'bottom'), "lower right": (0.95, 0.05, 'right', 'bottom')
            }
            x_pos, y_pos, ha, va = pos_map.get(tb_cfg['position'], (0.5, 0.5, 'center', 'center'))
            style_map = {'Rounded': 'round', 'Square': 'square', 'round,pad=1': 'round,pad=1', 'round4,pad=0.5': 'round4,pad=0.5'}
            boxstyle = style_map.get(tb_cfg['style'], 'round')
            
            lines.append(f"    ax.text({x_pos}, {y_pos}, {self._clean_value(tb_cfg['content'])}, transform=ax.transAxes,")
            lines.append(f"            fontsize=11, verticalalignment='{va}', horizontalalignment='{ha}',")
            lines.append(f"            bbox=dict(boxstyle={self._clean_value(boxstyle)}, facecolor={self._clean_value(tb_cfg['bg_color'])}, alpha=0.8, pad=1))")


        # --- 12. Final Touches ---
        lines.append("\n    # --- 12. Final Touches ---")
        if get_cfg("appearance.figure.tight_layout", True):
            lines.append("    try:")
            lines.append("        fig.tight_layout()")
            lines.append("    except Exception as e:")
            lines.append("        print(f'Tight layout failed: {{e}}')")
            
        lines.append("\n    print('Plot created successfully.')")
        lines.append("    return fig, ax")
        return "\n".join(lines)

    def _generate_main(self, export_type: str) -> str:
        """Generates the main execution block."""
        lines = [
            "\n",
            "if __name__ == '__main__':",
            "    print('--- DataPlot Studio Export Script ---')",
            "    # 1. Load Data",
            "    df_raw = load_data()",
            "",
            "    if df_raw is not None:",
            "        # 2. Process Data",
            "        df_processed = process_data(df_raw)",
            "        print(f'Processed data shape: {{df_processed.shape}}')",
            "        print('\\n', df_processed.head())",
            "",
            "        output_data_file = 'dps_processed_data.csv'",
            "        df_processed.to_csv(output_data_file, index=False)",
            "        print(f'\\nProcessed data saved to {{output_data_file}}')",
        ]
        
        if export_type == "Data + Plot":
            lines.extend([
                "",
                "        # 3. Create Plot",
                "        try:",
                "            fig, ax = create_plot(df_processed)",
                "            ",
                "            # 4. Save and Show Plot",
                "            output_plot_file = 'dps_exported_plot.png'",
                "            fig.savefig(output_plot_file, dpi=300, bbox_inches='tight')",
                "            print(f'\\nPlot saved to {{output_plot_file}}')",
                "            plt.show()",
                "            ",
                "        except Exception as e:",
                "            print(f'\\n--- PLOTTING FAILED ---')",
                "            print(f'An error occurred during plotting: {{e}}')",
                "            traceback.print_exc()",
            ])

        lines.extend([
            "",
            "    else:",
            "        print('Failed to load data, stopping script.')",
            "",
            "    print('--- Script execution finished ---')",
        ])
        return "\n".join(lines)

    def generate_full_script(self, 
                            df: pd.DataFrame,
                            data_filepath: str, 
                            source_info: Dict[str, Any], 
                            data_operations: List[Dict[str, Any]], 
                            plot_config: Dict[str, Any],
                            export_type: str = "Data + Plot"
                            ) -> str:
        """
        Generate complete script with both data manipulation and plotting.
        This is the main public method.
        """
        
        # 1. Add imports based on config
        self._add_imports(plot_config)
        
        # 2. Generate script sections
        header = self._generate_header()
        loader_func = self._generate_data_loader(data_filepath, source_info)
        processor_func = self._generate_data_ops(data_operations)
        
        plot_func = ""
        if export_type == "Data + Plot":
            plot_func = self._generate_plot_code(df, plot_config)
            
        main_block = self._generate_main(export_type)
        
        # 3. Combine all sections
        full_script = "\n\n".join(filter(None, [
            header,
            loader_func,
            processor_func,
            plot_func,
            main_block
        ]))
        
        return full_script

    def get_plot_script_only(self, df: pd.DataFrame, plot_config: Dict[str, Any]) -> str:
        """get the create_plot script for the script editor"""
        
        imports = [
            "import pandas as pd",
            "import numpy as np",
            "import matplotlib.pyplot as plt",
            "import seaborn as sns",
            "from matplotlib.ticker import MaxNLocator"
        ]

        if plot_config.get("axes", {}).get("datetime", {}).get("enabled"):
            imports.append("import matplotlib.dates as mdates")
        
        #scipy checks
        scatter_analysis = plot_config.get("advanced", {}).get("scatter", {})
        if scatter_analysis.get("show_regression") or \
        scatter_analysis.get("show_ci") or \
        scatter_analysis.get("show_r2") or \
        scatter_analysis.get("show_rmse") or \
        scatter_analysis.get("show_equation") or \
        scatter_analysis.get("error_bars", "None") != "None":
            imports.append("from scipy import stats")
            if scatter_analysis.get("show_ci"):
                imports.append("from scipy.stats import t as t_dist")
        
        hist_analysis = plot_config.get("advanced", {}).get("histogram", {})
        if hist_analysis.get("show_normal"):
            imports.append("from scipy.stats import norm")
        if hist_analysis.get("show_kde") or plot_config.get("plot_type") == "KDE":
            imports.append("from scipy.stats import gaussian_kde")

        import_block = "\n".join(imports)

        plot_func = self._generate_plot_code(df, plot_config)

        runner_comment = (
            "\n\n# --- Internal Runner ---\n"
            "# This function is called automatically when you click 'Run Script'.\n"
            "# It expects 'df' to be available in the local scope.\n"
        )

        return f"{import_block}\n\n{plot_func}{runner_comment}"