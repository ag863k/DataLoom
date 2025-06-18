import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, Any, List, Optional
import io
import base64

class DataAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
        self.datetime_columns = self._detect_datetime_columns()
    
    def _detect_datetime_columns(self) -> List[str]:
        datetime_cols = []
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                try:
                    pd.to_datetime(self.df[col].head(100), infer_datetime_format=True)
                    datetime_cols.append(col)
                except:
                    continue
        return datetime_cols
    
    def get_summary_stats(self) -> Dict[str, Any]:
        try:
            memory_usage = self.df.memory_usage(deep=True).sum()
        except Exception:
            memory_usage = 0
            
        summary = {
            'basic_info': {
                'rows': len(self.df),
                'columns': len(self.df.columns),
                'memory_usage': memory_usage,
                'missing_values': self.df.isnull().sum().sum()
            },
            'column_types': {
                'numeric': len(self.numeric_columns),
                'categorical': len(self.categorical_columns),
                'datetime': len(self.datetime_columns)
            },
            'numeric_summary': {},
            'categorical_summary': {},
            'missing_data': {}
        }
        
        if self.numeric_columns:
            numeric_stats = self.df[self.numeric_columns].describe()
            summary['numeric_summary'] = numeric_stats.to_dict()
        
        if self.categorical_columns:
            cat_summary = {}
            for col in self.categorical_columns[:5]:
                cat_summary[col] = {
                    'unique_values': self.df[col].nunique(),
                    'most_frequent': self.df[col].value_counts().head(3).to_dict()
                }
            summary['categorical_summary'] = cat_summary
        
        # Missing data analysis
        missing_data = self.df.isnull().sum()
        summary['missing_data'] = missing_data[missing_data > 0].to_dict()
        
        return summary
    
    def create_correlation_heatmap(self) -> Optional[go.Figure]:
        if len(self.numeric_columns) < 2:
            return None
        
        correlation_matrix = self.df[self.numeric_columns].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(correlation_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Correlation Heatmap',
            width=600,
            height=500
        )
        
        return fig
    
    def create_distribution_plots(self) -> List[go.Figure]:
        figures = []
        
        for col in self.numeric_columns[:6]:
            fig = px.histogram(
                self.df, 
                x=col, 
                nbins=30,
                title=f'Distribution of {col}',
                marginal='box'
            )
            fig.update_layout(height=400)
            figures.append(fig)
        
        return figures
    
    def create_categorical_plots(self) -> List[go.Figure]:
        figures = []
        
        for col in self.categorical_columns[:4]:
            value_counts = self.df[col].value_counts().head(10)
            
            fig = go.Figure(data=[
                go.Bar(x=value_counts.index, y=value_counts.values)
            ])
            
            fig.update_layout(
                title=f'Top 10 Values in {col}',
                xaxis_title=col,
                yaxis_title='Count',
                height=400
            )
            
            figures.append(fig)
        
        return figures
    
    def create_time_series_plot(self, date_col: str, value_col: str) -> Optional[go.Figure]:
        if date_col not in self.datetime_columns or value_col not in self.numeric_columns:
            return None
        
        try:
            df_ts = self.df.copy()
            df_ts[date_col] = pd.to_datetime(df_ts[date_col])
            df_ts = df_ts.sort_values(date_col)
            
            fig = px.line(
                df_ts, 
                x=date_col, 
                y=value_col,
                title=f'{value_col} over Time'
            )
            
            fig.update_layout(height=400)
            return fig
            
        except Exception:
            return None
    
    def create_scatter_plot(self, x_col: str, y_col: str, color_col: Optional[str] = None) -> Optional[go.Figure]:
        if x_col not in self.df.columns or y_col not in self.df.columns:
            return None
        
        try:
            fig = px.scatter(
                self.df,
                x=x_col,
                y=y_col,
                color=color_col if color_col and color_col in self.df.columns else None,
                title=f'{y_col} vs {x_col}'
            )
            
            fig.update_layout(height=400)
            return fig
            
        except Exception:
            return None
    
    def get_outliers(self, method: str = 'iqr') -> Dict[str, List]:
        outliers = {}
        
        for col in self.numeric_columns:
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outlier_indices = self.df[
                    (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                ].index.tolist()
                
                if outlier_indices:
                    outliers[col] = {
                        'count': len(outlier_indices),
                        'percentage': len(outlier_indices) / len(self.df) * 100,
                        'indices': outlier_indices[:10]
                    }
        
        return outliers
    
    def get_insights(self) -> List[Dict[str, str]]:
        """Generate key insights about the data"""
        insights = []
        
        # Basic insights
        insights.append({
            'type': 'Dataset Overview',
            'message': f"Dataset contains {len(self.df):,} rows and {len(self.df.columns)} columns"
        })
        
        # Missing data insights
        missing_pct = (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
        if missing_pct > 5:
            insights.append({
                'type': 'Data Quality',
                'message': f"{missing_pct:.1f}% of data is missing - consider data cleaning"
            })
        elif missing_pct > 0:
            insights.append({
                'type': 'Data Quality',
                'message': f"Low missing data rate: {missing_pct:.1f}%"
            })
        else:
            insights.append({
                'type': 'Data Quality',
                'message': "No missing data detected"
            })
        
        # Numeric data insights
        if self.numeric_columns:
            insights.append({
                'type': 'Numeric Analysis',
                'message': f"{len(self.numeric_columns)} numeric columns available for analysis"
            })
            
            # Check for highly correlated variables
            if len(self.numeric_columns) >= 2:
                corr_matrix = self.df[self.numeric_columns].corr()
                high_corr = np.where(np.abs(corr_matrix) > 0.8)
                high_corr_pairs = [(corr_matrix.index[x], corr_matrix.columns[y]) 
                                 for x, y in zip(*high_corr) if x != y and x < y]
                
                if high_corr_pairs:
                    insights.append({
                        'type': 'Correlation',
                        'message': f"Found {len(high_corr_pairs)} highly correlated variable pairs"
                    })
        
        # Categorical data insights
        if self.categorical_columns:
            insights.append({
                'type': 'Categorical Analysis',
                'message': f"{len(self.categorical_columns)} categorical columns for grouping analysis"
            })
            
            high_cardinality_cols = [col for col in self.categorical_columns 
                                   if self.df[col].nunique() > len(self.df) * 0.8]
            if high_cardinality_cols:
                insights.append({
                    'type': 'Data Cardinality',
                    'message': f"High cardinality detected in: {', '.join(high_cardinality_cols)}"
                })
        
        return insights
    
    def get_outliers(self) -> Dict[str, Dict[str, Any]]:
        """Detect outliers in numeric columns using IQR method"""
        outliers = {}
        
        for col in self.numeric_columns:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            outlier_count = outlier_mask.sum()
            outlier_percentage = (outlier_count / len(self.df)) * 100
            
            outliers[col] = {
                'count': outlier_count,
                'percentage': outlier_percentage,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }
        
        return outliers
    
    def generate_report(self) -> str:
        """Generate a comprehensive text report of the data analysis"""
        report = []
        report.append("=" * 50)
        report.append("DataLoom - Data Analysis Report")
        report.append("=" * 50)
        report.append("")
        
        # Basic information
        report.append("DATASET OVERVIEW")
        report.append("-" * 20)
        report.append(f"Rows: {len(self.df):,}")
        report.append(f"Columns: {len(self.df.columns)}")
        try:
            memory_mb = self.df.memory_usage(deep=True).sum() / 1024 / 1024
            report.append(f"Memory Usage: {memory_mb:.2f} MB")
        except Exception:
            report.append("Memory Usage: N/A")
        report.append("")
        
        # Column types
        report.append("COLUMN TYPES")
        report.append("-" * 20)
        report.append(f"Numeric: {len(self.numeric_columns)}")
        report.append(f"Categorical: {len(self.categorical_columns)}")
        report.append(f"DateTime: {len(self.datetime_columns)}")
        report.append("")
        
        # Missing data
        missing_data = self.df.isnull().sum()
        missing_data = missing_data[missing_data > 0]
        
        if not missing_data.empty:
            report.append("MISSING DATA")
            report.append("-" * 20)
            for col, count in missing_data.items():
                percentage = (count / len(self.df)) * 100
                report.append(f"{col}: {count} ({percentage:.1f}%)")
            report.append("")
        
        # Numeric summary
        if self.numeric_columns:
            report.append("NUMERIC COLUMNS SUMMARY")
            report.append("-" * 20)
            numeric_summary = self.df[self.numeric_columns].describe()
            for col in self.numeric_columns:
                report.append(f"\n{col}:")
                report.append(f"  Mean: {numeric_summary.loc['mean', col]:.2f}")
                report.append(f"  Median: {numeric_summary.loc['50%', col]:.2f}")
                report.append(f"  Std Dev: {numeric_summary.loc['std', col]:.2f}")
                report.append(f"  Min: {numeric_summary.loc['min', col]:.2f}")
                report.append(f"  Max: {numeric_summary.loc['max', col]:.2f}")
            report.append("")
        
        # Categorical summary
        if self.categorical_columns:
            report.append("CATEGORICAL COLUMNS SUMMARY")
            report.append("-" * 20)
            for col in self.categorical_columns:
                unique_count = self.df[col].nunique()
                most_common = self.df[col].mode().iloc[0] if not self.df[col].empty else "N/A"
                report.append(f"\n{col}:")
                report.append(f"  Unique Values: {unique_count}")
                report.append(f"  Most Common: {most_common}")
            report.append("")
        
        # Insights
        insights = self.get_insights()
        if insights:
            report.append("KEY INSIGHTS")
            report.append("-" * 20)
            for insight in insights:
                report.append(f"• {insight['type']}: {insight['message']}")
            report.append("")
        
        report.append("=" * 50)
        report.append("Report generated by DataLoom Analytics Platform")
        report.append("=" * 50)
        
        return "\n".join(report)
