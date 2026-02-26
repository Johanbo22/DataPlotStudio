import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import curve_fit
from scipy.stats import t as t_dist
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List

class RegressionType(Enum):
    LINEAR = "Linear"
    POLYNOMIAL = "Polynomial"
    EXPONENTIAL = "Exponential"
    LOGARITHMIC = "Logarithmic"

class ErrorBarType(Enum):
    NONE = "None"
    STANDARD_DEVIATION = "Standard Deviation"
    STANDARD_ERROR = "Standard Error"

@dataclass
class RegressionMetrics:
    r_squared: float
    rmse: float
    equation_str: str
    
@dataclass
class RegressionResult:
    x_line: np.ndarray
    y_line: np.ndarray
    y_pred_all: np.ndarray
    metrics: RegressionMetrics
    residuals: np.ndarray

class RegressionAnalyser:
    """Handles mathematcal modeling and statistics for dataset regression"""
    
    @staticmethod
    def clean_data(df: pd.DataFrame, x_col: str, y_col: str, reg_type: RegressionType) -> Tuple[np.ndarray, np.ndarray]:
        """Validates and extracts numeric vectors used for analysis"""
        if not pd.api.types.is_numeric_dtype(df[x_col]) or not pd.api.types.is_numeric_dtype(df[y_col]):
            raise TypeError(f"Columns {x_col} and {y_col} must be numeric")
        
        mask = np.isfinite(df[x_col]) & np.isfinite(df[y_col])
        if reg_type == RegressionType.LOGARITHMIC:
            mask &= (df[x_col] > 0)
        
        return df.loc[mask, x_col].values, df.loc[mask, y_col].values
    
    @staticmethod
    def compute_fit(x_data: np.ndarray, y_data: np.ndarray, reg_type: RegressionType, degree: int = 2) -> RegressionResult:
        """Computes a regression fit based on regression type"""
        x_line = np.linspace(x_data.min(), x_data.max(), 100)
        
        num_format = ".4g"
        
        if reg_type == RegressionType.POLYNOMIAL:
            coeffs = np.polyfit(x_data, y_data, degree)
            poly_func = np.poly1d(coeffs)
            y_pred_all = poly_func(x_data)
            y_line = poly_func(x_line)
            
            terms = []
            for i, coefficient in enumerate(coeffs):
                power = degree - i
                formatted_coeff = f"{coefficient:{num_format}}"
                if power == 0:
                    terms.append(f"{formatted_coeff}")
                elif power == 1:
                    terms.append(f"{formatted_coeff}x")
                else:
                    terms.append(f"{formatted_coeff}x^{power}")
            equation_str = " + ".join(terms).replace("+ -", "- ")
        
        elif reg_type == RegressionType.EXPONENTIAL:
            def exp_func(x, a, b):
                return a * np.exp(b * x)
            popt, _ = curve_fit(exp_func, x_data, y_data, p0=(1, 1e-6), maxfev=10000)
            y_pred_all = exp_func(x_data, *popt)
            y_line = exp_func(x_line, *popt)
            equation_str = f"{popt[0]:{num_format}} * exp({popt[1]:{num_format}} * x)"
        
        elif reg_type == RegressionType.LOGARITHMIC:
            def log_func(x, a, b):
                return a + b * np.log(x)
            popt, _ = curve_fit(log_func, x_data, y_data)
            y_pred_all = log_func(x_data, *popt)
            y_line = log_func(x_line, *popt)
            equation_str = f"{popt[0]:{num_format}} + {popt[1]:{num_format}} * ln(x)"
        else:
            slope, intercept, _, _, _ = stats.linregress(x_data, y_data)
            y_pred_all = slope * x_data + intercept
            y_line = slope * x_line + intercept
            equation_str = f"{slope:{num_format}}x {'+' if intercept >= 0 else '-'} {abs(intercept):{num_format}}"
        
        residuals = y_data - y_pred_all
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y_data - np.mean(y_data))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
        rmse = np.sqrt(np.mean(residuals**2))
        
        metrics = RegressionMetrics(r_squared=r_squared, rmse=rmse, equation_str=equation_str)
        return RegressionResult(x_line, y_line, y_pred_all, metrics, residuals)
    
    @staticmethod
    def compute_confidence_interval(x_data: np.ndarray, residuals: np.ndarray, x_line: np.ndarray, confidence_level: float) -> np.ndarray:
        n = len(x_data)
        if n <= 2:
            return np.zeros_like(x_line)
        
        residual_std = np.sqrt(np.sum(residuals**2) / (n - 2))
        x_mean = np.mean(x_data)
        
        se_line = residual_std * np.sqrt(1/n + (x_line - x_mean)**2 / np.sum((x_data - x_mean)**2))
        t_val = t_dist.ppf((1 + confidence_level) / 2, n - 2)
        return t_val * se_line
    
    @staticmethod
    def compute_error_bars_std(x_data: np.ndarray, y_data: np.ndarray, residuals: np.ndarray, n_bins: int = 20) -> Tuple[List[float], List[float], List[float]]:
        n_bins = min(n_bins, len(x_data) // 5)
        if n_bins <= 1:
            return [], [], []
        
        sorted_indices = np.argsort(x_data)
        x_sorted, y_sorted, residuals_sorted = x_data[sorted_indices], y_data[sorted_indices], residuals[sorted_indices]
        
        bin_size = len(x_data) // n_bins
        x_centers, y_centers, y_errors = [], [], []
        
        for i in range(n_bins):
            start = i * bin_size
            end = start + bin_size if i < n_bins - 1 else len(x_data)
            
            if end - start > 1:
                x_centers.append(float(np.mean(x_sorted[start:end])))
                y_centers.append(float(np.mean(y_sorted[start:end])))
                y_errors.append(float(np.std(residuals_sorted[start:end])))
        
        return x_centers, y_centers, y_errors
    
    @staticmethod
    def compute_error_bars_se(x_data: np.ndarray, residuals: np.ndarray) -> np.ndarray:
        n = len(x_data)
        residual_std = np.sqrt(np.sum(residuals**2) / (n - 2)) if n > 2 else 0
        x_mean = np.mean(x_data)
        sum_sq_diff = np.sum((x_data - x_mean)**2)
        
        if sum_sq_diff == 0:
            return np.zeros_like(x_data)
        return residual_std * np.sqrt(1/n + (x_data - x_mean)**2 / sum_sq_diff)