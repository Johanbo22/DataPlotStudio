# core/code_exporter.py
from typing import Dict, Any, List, Set
from datetime import datetime
from pathlib import Path
import pandas as pd

class CodeExporter:
    """
    Generates a complete, runnable Python script by inspecting
    the final UI state of the DataHandler and PlotTab.
    """
    
    def __init__(self) -> None:
        self.imports: Set[str] = set()
        self.script_lines: List[str] = []

    def _add_imports(self, plot_config: Dict[str, Any]) -> None:
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
            "\"\"\"",
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
            lines.append("    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'")
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
                    lines.append("        # Attempt numeric conversion for filter value")
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
            lines.append("            stats_text.append(f'{eq_y} = {slope:.4f}{eq_x} {op} {abs(intercept):.4f}')")
        if scatter_cfg.get("show_r2"):
            lines.append("            stats_text.append(f'R² = {r_value**2:.4f}')")
        if scatter_cfg.get("show_rmse"):
            lines.append("            y_pred = slope * x_data_raw + intercept")
            lines.append("            rmse = np.sqrt(np.mean((y_data_raw - y_pred)**2))")
            lines.append("            stats_text.append(f'RMSE = {rmse:.4f}')")
        
        
        lines.append("            if stats_text:")
        lines.append("                textstr = '\\n'.join(stats_text)")
        lines.append("                props = dict(boxstyle='round', facecolor='wheat', alpha=0.85)")
        lines.append(f"                ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=11, verticalalignment='top', bbox=props, fontfamily={self._clean_value(get_cfg('appearance.font_family', 'Arial'))})")

        error_bar_type = scatter_cfg.get("error_bars", "None")
        if error_bar_type == "Standard Deviation":
            lines.append("            # (Standard Deviation error bar export is complex, skipping for now)") # Per-bin logic
        
        elif error_bar_type == "Standard Error":
            lines.append("            # Add Standard Error bars")
            lines.append("            y_pred_all = slope * x_data_raw + intercept")
            lines.append("            residuals = y_data_raw - y_pred_all")
            lines.append("            residual_std = np.sqrt(np.sum(residuals**2) / (len(x_data_raw) - 2))")
            lines.append("            x_mean = np.mean(x_data_raw)")
            lines.append("            se_points = residual_std * np.sqrt(1/len(x_data_raw) + (x_data_raw - x_mean)**2 / np.sum((x_data_raw - x_mean)**2))")
            lines.append("            step = max(1, len(x_data_raw) // 30)")
            lines.append("            err_args = (x_data_raw[::step], y_data_raw[::step])")
            lines.append(f"            err_kwargs = {{'yerr': se_points[::step]}} if not {flip_axes} else {{'xerr': se_points[::step]}}")
            lines.append("            ax.errorbar(*err_args, **err_kwargs, fmt='o', ecolor='gray', markersize=3, alpha=0.5, capsize=4, zorder=8, markerfacecolor='none', markeredgecolor='none', elinewidth=1, linestyle='none')")


        lines.append("    except Exception as e:")
        lines.append("        print(f'Failed to add scatter analysis: {{e}}')")
        lines.append("        traceback.print_exc()")
        
        return lines

    def _get_cfg(self, config: Dict[str, Any], path: str, default: Any = None) -> Any:
        """Get the information nested in config using dot notation
        fx., want to get the config["axes"]["x_axis"]["min"] -> "axes.x_axis.min
        """
        keys = path.split(".")
        val = config
        try:
            for key in keys:
                val = val[key]
            return val
        except (KeyError, TypeError, AttributeError):
            return default
    
    def _generate_figure_setup(self, config: Dict[str, Any]) -> List[str]:
        """Generate the code for the figure initialization and global styling params"""
        lines = ["\n    # --- 1. Set up Figure and Style ---"]
        
        style = self._clean_value(self._get_cfg(config, "appearance.figure.style", "default"))
        lines.append("    try:")
        lines.append(f"        plt.style.use({style})")
        lines.append("    except Exception: plt.style.use('default')")

        font_family = self._clean_value(self._get_cfg(config, 'appearance.font_family', 'Arial'))
        lines.append(f"    plt.rcParams['font.family'] = {font_family}")

        width = self._get_cfg(config, 'appearance.figure.width', 10)
        height = self._get_cfg(config, 'appearance.figure.height', 6)
        dpi = self._get_cfg(config, 'appearance.figure.dpi', 100)
        
        lines.append(f"    fig, ax = plt.subplots(figsize=({width}, {height}), dpi={dpi})")
        
        bg_color = self._clean_value(self._get_cfg(config, 'appearance.figure.bg_color', 'white'))
        face_color = self._clean_value(self._get_cfg(config, 'appearance.figure.face_color', 'white'))
        
        if bg_color != "'white'": lines.append(f"    fig.set_facecolor({bg_color})")
        if face_color != "'white'": lines.append(f"    ax.set_facecolor({face_color})")
        
        return lines
    
    def _generate_data_prep(self, df: pd.DataFrame, config: Dict[str, Any], x_col: str, y_cols: List[str]) -> List[str]:
        """Generate the code used to preprare datetime data"""
        lines = ["\n    # --- 2. Data Preparation ---"]
        
        cols_to_convert = []
        
        if x_col and x_col in df.columns:
            if "datetime" in str(df.dtypes.get(x_col, '')):
                cols_to_convert.append(x_col)
        
        for y_c in y_cols:
            if y_c in df.columns and "datetime" in str(df.dtypes.get(y_c, '')):
                cols_to_convert.append(y_c)
        
        if cols_to_convert:
            lines.append("    # Convert detected datetime columns")
            lines.append("    try:")
            for col in set(cols_to_convert):
                lines.append(f"        df[{self._clean_value(col)}] = pd.to_datetime(df[{self._clean_value(col)}], errors='coerce', utc=True)")
            lines.append("    except Exception as e: print(f'Warning: Date conversion failed: {{e}}')")
        
        if self._get_cfg(config, "basic.use_subset"):
            subset_name = self._clean_value(self._get_cfg(config, "basic.subset_name"))
            lines.append(f"    print(f'Note: processing full dataset, but UI was viewing subset: {{ {subset_name} }}')")

        return lines
    
    def _generate_plot_dispatch(self, config: Dict[str, Any], x_col: str, y_cols: List[str], hue: str, palette: str) -> List[str]:
        """Method to call the specific plot generation based on plo ttype"""
        lines = ["\n    # --- 3. Generate Plot ---"]
        plot_type = self._get_cfg(config, "plot_type", "Scatter")
        lines.append(f"    # Plot Type: {plot_type}")

        alpha = self._get_cfg(config, "advanced.global_alpha", 1.0)
        flip = self._get_cfg(config, "axes.flip_axes", False)
        
        # Map simple variables for generators
        ctx = {
            "x": x_col, 
            "y": self._clean_value(y_cols[0]) if y_cols else None,
            "ys": self._clean_value(y_cols),
            "y_list": y_cols,
            "hue": self._clean_value(hue) if hue and hue != "None" else "None",
            "palette": self._clean_value(palette),
            "alpha": alpha,
            "flip": flip,
            "config": config
        }
        if plot_type == "Line":
            lines.extend(self._generate_line_plot(ctx))
        elif plot_type == "Scatter":
            lines.extend(self._generate_scatter_plot(ctx))
        elif plot_type == "Bar":
            lines.extend(self._generate_bar_plot(ctx))
        elif plot_type == "Histogram":
            lines.extend(self._generate_histogram(ctx))
        elif plot_type == "Box":
            lines.extend(self._generate_box_plot(ctx))
        elif plot_type == "Violin":
            lines.extend(self._generate_violin_plot(ctx))
        elif plot_type == "Area":
            lines.extend(self._generate_area_plot(ctx))
        elif plot_type == "Pie":
            lines.extend(self._generate_pie_chart(ctx))
        elif plot_type == "Heatmap":
            lines.extend(self._generate_heatmap(ctx))
        elif plot_type == "KDE":
            lines.extend(self._generate_kde_plot(ctx))
        elif plot_type in ["Hexbin", "2D Density", "2D Histogram"]:
            lines.extend(self._generate_2d_distribution(ctx, plot_type))
        elif plot_type in ["Stem", "Stairs", "Eventplot", "ECDF", "Stackplot"]:
            lines.extend(self._generate_specialty_plot(ctx, plot_type))
        elif plot_type in ["Image Show (imshow)", "pcolormesh", "Contour", "Contourf"]:
            lines.extend(self._generate_gridded_plot(ctx, plot_type))
        elif plot_type in ["Barbs", "Quiver", "Streamplot"]:
            lines.extend(self._generate_vector_plot(ctx, plot_type))
        elif plot_type in ["Tricontour", "Tricontourf", "Tripcolor", "Triplot"]:
            lines.extend(self._generate_tri_plot(ctx, plot_type))
        elif plot_type == "GeoSpatial":
            lines.extend(self._generate_geospatial_plot(ctx))
        else:
            # Fallback to scatter if something fails
            lines.append(f"    sns.scatterplot(data=df, x={ctx['x']}, y={ctx['y']}, alpha={alpha})")
        
        return lines
    
    def _generate_line_plot(self, ctx: Dict) -> List[str]:
        lines = []
        g_line = self._get_cfg(ctx["config"], "advanced.global_line", {})
        g_marker = self._get_cfg(ctx["config"], "advanced.global_marker", {})

        marker = self._clean_value(g_marker.get("shape", "None"))
        marker = f"{marker} if {marker} != 'None' else None"

        kwargs = [
            f"marker={marker}",
            f"markersize={g_marker.get('size', 6)}",
            f"linestyle={self._clean_value(g_line.get('style', '-'))}",
            f"linewidth={g_line.get('width', 1.5)}",
            f"alpha={ctx['alpha']}"
        ]
        kwargs_str = ", ".join(kwargs)
        if ctx['hue'] != "None":
            lines.append(f"    groups = df[{ctx['hue']}].unique()")
            lines.append("    for group in groups:")
            lines.append(f"        mask = df[{ctx['hue']}] == group")
            lines.append(f"        for col in {ctx['ys']}:")
            lines.append("            # Plot with Hue")
            plot_cmd = f"ax.plot(df.loc[mask, {ctx['x']}], df.loc[mask, col], label=f'{{col}} - {{group}}', {kwargs_str})"
            if ctx['flip']:
                plot_cmd = f"ax.plot(df.loc[mask, col], df.loc[mask, {ctx['x']}], label=f'{{col}} - {{group}}', {kwargs_str})"
            lines.append(f"            {plot_cmd}")
        else:
            lines.append(f"    for col in {ctx['ys']}:")
            plot_cmd = f"ax.plot(df[{ctx['x']}], df[col], label=col, {kwargs_str})"
            if ctx['flip']:
                plot_cmd = f"ax.plot(df[col], df[{ctx['x']}], label=col, {kwargs_str})"
            lines.append(f"        {plot_cmd}")
        return lines
    
    def _generate_scatter_plot(self, ctx: Dict) -> List[str]:
        lines = []
        g_marker = self._get_cfg(ctx['config'], "advanced.global_marker", {})
        size = g_marker.get('size', 6)
        
        kw = []
        if ctx['hue'] != "None":
            x_var, y_var = (ctx['x'], ctx['y']) if not ctx['flip'] else (ctx['y'], ctx['x'])
            kw.append(f"data=df, x={x_var}, y={y_var}")
            kw.append(f"hue={ctx['hue']}, palette={ctx['palette']}")
            kw.append(f"s={size}**2, alpha={ctx['alpha']}, ax=ax")
            
            marker = self._clean_value(g_marker.get('shape', 'o'))
            if marker != "'None'": kw.append(f"marker={marker}")
            
            lines.append(f"    sns.scatterplot({', '.join(kw)})")
        else:
            x_var, y_var = (f"df[{ctx['x']}]", f"df[{ctx['y']}]") if not ctx['flip'] else (f"df[{ctx['y']}]", f"df[{ctx['x']}]")
            kw.append(f"x={x_var}, y={y_var}")
            kw.append(f"label={ctx['y']}")
            kw.append(f"s={size}**2, alpha={ctx['alpha']}")
            
            marker = self._clean_value(g_marker.get('shape', 'o'))
            if marker != "'None'": kw.append(f"marker={marker}")
            
            edge = self._clean_value(g_marker.get('edge_color'))
            if edge != "'Auto'": kw.append(f"edgecolors={edge}")
            
            c = self._clean_value(g_marker.get('color'))
            if c != "'Auto'": kw.append(f"c={c}")

            lines.append(f"    ax.scatter({', '.join(kw)})")

        return lines
    
    def _generate_bar_plot(self, ctx: Dict) -> List[str]:
        lines = []
        g_bar = self._get_cfg(ctx['config'], "advanced.global_bar", {})
        width = g_bar.get('width', 0.8)
        
        if ctx['hue'] != "None" and len(ctx['y_list']) == 1:
            orient = "'h'" if ctx['flip'] else "'v'"
            x_var, y_var = (ctx['x'], ctx['y']) if not ctx['flip'] else (ctx['y'], ctx['x'])
            
            lines.append(f"    sns.barplot(data=df, x={x_var}, y={y_var}, hue={ctx['hue']},")
            lines.append(f"                orient={orient}, palette={ctx['palette']}, alpha={ctx['alpha']}, ax=ax)")
        else:
            lines.append(f"    x_labels = df[{ctx['x']}].unique()")
            lines.append("    x_pos = np.arange(len(x_labels))")
            lines.append(f"    bar_width = {width} / {len(ctx['y_list'])}")
            
            lines.append(f"    for i, col in enumerate({ctx['ys']}):")
            lines.append(f"        offset = (i - {len(ctx['y_list'])}/2) * bar_width + bar_width/2")
            lines.append(f"        vals = [df[df[{ctx['x']}]==l][col].values[0] if not df[df[{ctx['x']}]==l].empty else 0 for l in x_labels]")
            
            if ctx['flip']:
                lines.append(f"        ax.barh(x_pos + offset, vals, height=bar_width, label=col, alpha={ctx['alpha']})")
                lines.append("    ax.set_yticks(x_pos)")
                lines.append("    ax.set_yticklabels(x_labels)")
            else:
                lines.append(f"        ax.bar(x_pos + offset, vals, width=bar_width, label=col, alpha={ctx['alpha']})")
                lines.append("    ax.set_xticks(x_pos)")
                lines.append("    ax.set_xticklabels(x_labels)")
        return lines
    
    def _generate_histogram(self, ctx: Dict) -> List[str]:
        lines = []
        hist_cfg = self._get_cfg(ctx['config'], "advanced.histogram", {})
        bins = hist_cfg.get('bins', 30)
        density = "True" if hist_cfg.get('show_normal') or hist_cfg.get('show_kde') else "False"
        
        lines.append(f"    data = df[{ctx['y']}].dropna()")
        lines.append(f"    _, bins, _ = ax.hist(data, bins={bins}, density={density}, alpha={ctx['alpha']}, label='Histogram')")
        
        if hist_cfg.get('show_normal'):
            lines.append("    # Overlay Normal Distribution")
            lines.append("    mu, sigma = data.mean(), data.std()")
            lines.append("    y_norm = norm.pdf(np.linspace(bins[0], bins[-1], 100), mu, sigma)")
            lines.append("    ax.plot(np.linspace(bins[0], bins[-1], 100), y_norm, 'r-', lw=2, label='Normal Dist')")
            
        if hist_cfg.get('show_kde'):
            lines.append("    # Overlay KDE")
            lines.append("    kde = gaussian_kde(data)")
            lines.append("    x_kde = np.linspace(bins[0], bins[-1], 100)")
            lines.append("    ax.plot(x_kde, kde(x_kde), 'g--', lw=2, label='KDE')")
            
        return lines
    
    def _generate_box_plot(self, ctx: Dict) -> List[str]:
        vert = str(not ctx['flip'])
        return [f"    df.boxplot(column={ctx['ys']}, ax=ax, vert={vert})"]

    def _generate_violin_plot(self, ctx: Dict) -> List[str]:
        x_var, y_var = (ctx['x'], ctx['y']) if not ctx['flip'] else (ctx['y'], ctx['x'])
        orient = "'h'" if ctx['flip'] else "'v'"
        return [f"    sns.violinplot(data=df, x={x_var}, y={y_var}, hue={ctx['hue']}, orient={orient}, palette={ctx['palette']}, ax=ax)"]

    def _generate_area_plot(self, ctx: Dict) -> List[str]:
        lines = []
        lines.append("    try:")
        lines.append(f"        df_plot = df.set_index({ctx['x']})[{ctx['ys']}]")
        lines.append(f"        if {ctx['flip']}:")
        lines.append("            # Area plot doesn't support direct flip in pandas, using fill_betweenx manually")
        lines.append(f"            for col in {ctx['ys']}:")
        lines.append(f"                ax.fill_betweenx(df_plot.index, 0, df_plot[col], label=col, alpha={ctx['alpha']})")
        lines.append("        else:")
        lines.append(f"            df_plot.plot(kind='area', stacked=True, alpha={ctx['alpha']}, colormap={ctx['palette']}, ax=ax)")
        lines.append("    except Exception as e: print(f'Area plot error: {{e}}')")
        return lines

    def _generate_pie_chart(self, ctx: Dict) -> List[str]:
        lines = []
        pie_cfg = self._get_cfg(ctx['config'], "advanced.pie", {})
        lines.append("    try:")
        lines.append(f"        data = df.groupby({ctx['x']})[{ctx['y']}].sum()")
        
        explode_list = "None"
        if pie_cfg.get("explode_first"):
             dist = pie_cfg.get("explode_distance", 0.1)
             lines.append("        explode = [0.0] * len(data)")
             lines.append(f"        if explode: explode[0] = {dist}")
             explode_list = "explode"
             
        autopct = "'%1.2f%%'" if pie_cfg.get("show_percentages") else "None"
        start = pie_cfg.get("start_angle", 0)
        shadow = pie_cfg.get("shadow", False)
        
        lines.append(f"        ax.pie(data, labels=data.index, autopct={autopct}, startangle={start}, explode={explode_list}, shadow={shadow})")
        lines.append("        ax.set_ylabel('')")
        lines.append("    except Exception as e: print(f'Pie chart error: {{e}}')")
        return lines
    
    def _generate_heatmap(self, ctx: Dict) -> List[str]:
        return [
            "    # Heatmap of correlations",
            "    numeric = df.select_dtypes(include=[np.number])",
            f"    sns.heatmap(numeric.corr(), annot=True, cmap={ctx['palette']}, ax=ax)"
        ]

    def _generate_kde_plot(self, ctx: Dict) -> List[str]:
        return [f"    df[{ctx['y']}].plot(kind='kde', ax=ax, alpha={ctx['alpha']})"]

    def _generate_2d_distribution(self, ctx: Dict, plot_type: str) -> List[str]:
        lines = []
        if plot_type == "Hexbin":
            x_v, y_v = (ctx['x'], ctx['y']) if not ctx['flip'] else (ctx['y'], ctx['x'])
            lines.append(f"    ax.hexbin(df[{x_v}], df[{y_v}], gridsize=20, cmap={ctx['palette']})")
        elif plot_type == "2D Density":
            lines.append(f"    sns.kdeplot(data=df, x={ctx['x']}, y={ctx['y']}, fill=True, cmap={ctx['palette']}, ax=ax)")
        elif plot_type == "2D Histogram":
             lines.append(f"    h = ax.hist2d(df[{ctx['x']}], df[{ctx['y']}], cmap={ctx['palette']})")
             lines.append("    fig.colorbar(h[3], ax=ax)")
        return lines
    
    def _generate_specialty_plot(self, ctx: Dict, plot_type: str) -> List[str]:
        lines = []
        if plot_type == "Stem":
            lines.append(f"    ax.stem(df[{ctx['x']}], df[{ctx['y']}])")
        elif plot_type == "Stairs":
            lines.append(f"    ax.stairs(df[{ctx['y']}], edges=np.arange(len(df)+1)) # Approximation")
        elif plot_type == "Eventplot":
             lines.append("    # Eventplot expects list of lists")
             lines.append(f"    data = [df[c].dropna().values for c in {ctx['ys']}]")
             lines.append(f"    ax.eventplot(data, alpha={ctx['alpha']})")
        elif plot_type == "ECDF":
             lines.append(f"    ax.ecdf(df[{ctx['y']}])")
        elif plot_type == "Stackplot":
             lines.append("    # Ensure sorted X")
             lines.append(f"    dfs = df.sort_values(by={ctx['x']})")
             lines.append(f"    ax.stackplot(dfs[{ctx['x']}], dfs[{ctx['ys']}].T, labels={ctx['ys']}, alpha={ctx['alpha']})")
             lines.append("    ax.legend(loc='upper left')")
        return lines
    
    def _generate_gridded_plot(self, ctx: Dict, plot_type: str) -> List[str]:
        lines = []
        z = self._clean_value(ctx['y_list'][1] if len(ctx['y_list']) > 1 else None)
        if z == "None": return ["    print('Error: Z-axis column missing for gridded plot')"]
        
        lines.append("    # Prepare Gridded Data")
        lines.append(f"    piv = df.pivot_table(index={ctx['y']}, columns={ctx['x']}, values={z}, aggfunc='mean')")
        lines.append("    X, Y = np.meshgrid(piv.columns, piv.index)")
        lines.append("    Z = piv.values")
        
        if plot_type == "Image Show (imshow)":
            lines.append(f"    im = ax.imshow(Z, origin='lower', aspect='auto', cmap={ctx['palette']})")
            lines.append("    fig.colorbar(im, ax=ax)")
        elif plot_type == "Contour":
            lines.append(f"    ax.contour(X, Y, Z, cmap={ctx['palette']})")
        elif plot_type == "Contourf":
            lines.append(f"    cf = ax.contourf(X, Y, Z, cmap={ctx['palette']})")
            lines.append("    fig.colorbar(cf, ax=ax)")
        elif plot_type == "pcolormesh":
            lines.append(f"    pcm = ax.pcolormesh(X, Y, Z, cmap={ctx['palette']})")
            lines.append("    fig.colorbar(pcm, ax=ax)")
            
        return lines
    
    def _generate_vector_plot(self, ctx: Dict, plot_type: str) -> List[str]:
        lines = []
        if len(ctx['y_list']) < 3: return ["    print('Error: Need U and V columns for vector plot')"]
        u, v = self._clean_value(ctx['y_list'][1]), self._clean_value(ctx['y_list'][2])
        
        if plot_type == "Quiver":
            lines.append(f"    ax.quiver(df[{ctx['x']}], df[{ctx['y']}], df[{u}], df[{v}])")
        elif plot_type == "Barbs":
            lines.append(f"    ax.barbs(df[{ctx['x']}], df[{ctx['y']}], df[{u}], df[{v}])")
        elif plot_type == "Streamplot":
             lines.append("    # Streamplot requires grid")
             lines.append("    # (Assuming simple grid logic similar to contour for export brevity)")
             lines.append("    print('Note: Streamplot export assumes data is griddable')")
        return lines
    
    def _generate_tri_plot(self, ctx: Dict, plot_type: str) -> List[str]:
        lines = []
        z = self._clean_value(ctx['y_list'][1] if len(ctx['y_list']) > 1 else None)
        
        if plot_type == "Triplot":
            lines.append(f"    ax.triplot(df[{ctx['x']}], df[{ctx['y']}])")
        elif z != "None":
            if plot_type == "Tricontour":
                lines.append(f"    ax.tricontour(df[{ctx['x']}], df[{ctx['y']}], df[{z}], cmap={ctx['palette']})")
            elif plot_type == "Tricontourf":
                lines.append(f"    tc = ax.tricontourf(df[{ctx['x']}], df[{ctx['y']}], df[{z}], cmap={ctx['palette']})")
                lines.append("    fig.colorbar(tc, ax=ax)")
        return lines
    
    def _generate_geospatial_plot(self, ctx: Dict) -> List[str]:
        lines = []
        lines.append("    try:")
        lines.append("        import geopandas as gpd")
        lines.append("        if 'geometry' not in df.columns:")
        lines.append("            print('Error: No geometry column found for geospatial plot')")
        lines.append("        else:")
        lines.append("            gdf = gpd.GeoDataFrame(df, geometry='geometry')")
        
        col = ctx['y'] if ctx['y'] != "None" else "None"
        scheme = self._clean_value(self._get_cfg(ctx['config'], "advanced.geospatial.scheme", "quantiles"))
        
        if col != "None":
             lines.append(f"            gdf.plot(column={col}, ax=ax, legend=True, scheme={scheme}, cmap={ctx['palette']})")
        else:
             lines.append("            gdf.plot(ax=ax)")
             
        if self._get_cfg(ctx['config'], "advanced.geospatial.axis_off"):
            lines.append("            ax.set_axis_off()")
            
        lines.append("    except ImportError:")
        lines.append("        print('Error: geopandas not installed')")
        return lines
    
    def _generate_appearance(self, config: Dict[str, Any], x_col: str, y_cols: List[str]) -> List[str]:
        """Generate the code used for axis labels, titles, spines etc"""
        lines = ["\n    # --- 4. Appearance & Labels ---"]
        
        # Explicitly fetch font family again to pass to specific label setters
        font_family = self._clean_value(self._get_cfg(config, 'appearance.font_family', 'Arial'))
        
        # Labels
        labels = {
            "title": (self._get_cfg(config, "appearance.title.text", ""), self._get_cfg(config, "appearance.title.enabled", True)),
            "xlabel": (self._get_cfg(config, "appearance.xlabel.text", x_col), self._get_cfg(config, "appearance.xlabel.enabled", True)),
            "ylabel": (self._get_cfg(config, "appearance.ylabel.text", y_cols[0] if y_cols else "Value"), self._get_cfg(config, "appearance.ylabel.enabled", True))
        }
        
        for kind, (text, enabled) in labels.items():
            if enabled:
                text_clean = self._clean_value(text)
                size = self._get_cfg(config, f"appearance.{kind}.size", 12)
                weight = self._clean_value(self._get_cfg(config, f"appearance.{kind}.weight", 'normal'))
                lines.append(f"    ax.set_{kind}({text_clean}, fontsize={size}, fontweight={weight})")
            else:
                lines.append(f"    ax.set_{kind}('')")
                
        # Spines
        lines.append("")
        for spine in ['top', 'bottom', 'left', 'right']:
            visible = self._get_cfg(config, f"appearance.spines.{spine}.visible", True)
            if not visible:
                lines.append(f"    ax.spines['{spine}'].set_visible(False)")
            else:
                color = self._clean_value(self._get_cfg(config, f"appearance.spines.{spine}.color", 'black'))
                width = self._get_cfg(config, f"appearance.spines.{spine}.width", 1.0)
                if color != "'black'": lines.append(f"    ax.spines['{spine}'].set_color({color})")
                if width != 1.0: lines.append(f"    ax.spines['{spine}'].set_linewidth({width})")

        return lines
    
    def _generate_axes_config(self, config: Dict[str, Any]) -> List[str]:
        """Generate scales, limits, and grids."""
        lines = ["\n    # --- 5. Axes & Grid ---"]
        
        # Scales
        lines.append(f"    ax.set_xscale({self._clean_value(self._get_cfg(config, 'axes.x_axis.scale', 'linear'))})")
        lines.append(f"    ax.set_yscale({self._clean_value(self._get_cfg(config, 'axes.y_axis.scale', 'linear'))})")
        
        # Limits
        if not self._get_cfg(config, "axes.x_axis.auto_limits", True):
             lines.append(f"    ax.set_xlim({self._get_cfg(config, 'axes.x_axis.min')}, {self._get_cfg(config, 'axes.x_axis.max')})")
        if not self._get_cfg(config, "axes.y_axis.auto_limits", True):
             lines.append(f"    ax.set_ylim({self._get_cfg(config, 'axes.y_axis.min')}, {self._get_cfg(config, 'axes.y_axis.max')})")
             
        # Invert
        if self._get_cfg(config, "axes.x_axis.invert"): lines.append("    ax.invert_xaxis()")
        if self._get_cfg(config, "axes.y_axis.invert"): lines.append("    ax.invert_yaxis()")

        # Grid
        if self._get_cfg(config, "grid.enabled"):
             which = self._clean_value(self._get_cfg(config, "grid.global.which", "major"))
             lines.append(f"    ax.grid(True, which={which}, alpha={self._get_cfg(config, 'grid.global.alpha', 0.5)})")
        else:
             lines.append("    ax.grid(False)")

        return lines

    def _generate_legend(self, config: Dict[str, Any]) -> List[str]:
        """Generate legend configuration."""
        lines = []
        if self._get_cfg(config, "legend.enabled", False):
            loc = self._clean_value(self._get_cfg(config, "legend.location", "best"))
            lines.append(f"    ax.legend(loc={loc})")
        return lines
    
    def _generate_plot_code(self, df: pd.DataFrame, plot_config: Dict[str, Any]) -> str:
        """Generation of the main plotting code"""

        x_col = self._clean_value(self._get_cfg(plot_config, "basic.x_column"))
        y_cols_raw = self._get_cfg(plot_config, "basic.y_columns", [])
        hue = self._get_cfg(plot_config, "basc.hue_column")
        palette = self._get_cfg(plot_config, "appearance.figure.palette", "deep")

        lines = [
            "", 
            "def create_plot(df):", 
            "    \"\"\"Create the visualization.\"\"\""
        ]

        # Setup part
        lines.extend(self._generate_figure_setup(plot_config))

        # Data preparation
        lines.extend(self._generate_data_prep(df, plot_config, self._get_cfg(plot_config, "basic.x_column"), y_cols_raw))

        # Plot dispatch
        lines.extend(self._generate_plot_dispatch(plot_config, x_col, y_cols_raw, hue, palette))

        # Add scatter analysis 
        if self._get_cfg(plot_config, "plot_type") == "Scatter":
            get_cfg_wrapper = lambda p, d=None: self._get_cfg(plot_config, p, d)
            flip = self._get_cfg(plot_config, "axes.flip_axes", False)
            y_str = self._clean_value(y_cols_raw[0] if y_cols_raw else "None")
            lines.extend(self._generate_scatter_analysis(get_cfg_wrapper, x_col, y_str, flip))
        
        # Styling
        lines.extend(self._generate_appearance(plot_config, self._get_cfg(plot_config, "basic.x_column"), y_cols_raw))
        lines.extend(self._generate_axes_config(plot_config))
        lines.extend(self._generate_legend(plot_config))

        # End
        lines.append("\n    try: fig.tight_layout()")
        lines.append("    except: pass")
        lines.append("\n    return fig, ax")
        
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
        """
    
        self._add_imports(plot_config)
        
        header = self._generate_header()
        loader_func = self._generate_data_loader(data_filepath, source_info)
        processor_func = self._generate_data_ops(data_operations)
        
        plot_func = ""
        if export_type == "Data + Plot":
            plot_func = self._generate_plot_code(df, plot_config)
            
        main_block = self._generate_main(export_type)
        
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