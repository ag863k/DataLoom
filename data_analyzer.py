import pandas as pd
import numpy as np
from typing import Dict, Any, List

class DataAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
        self.categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.datetime_columns = self._detect_datetime_columns()

    def _detect_datetime_columns(self) -> List[str]:
        datetime_cols = []
        for col in self.df.columns:
            if self.df[col].dtype == 'object':
                try:
                    pd.to_datetime(self.df[col].dropna().sample(min(10, len(self.df[col].dropna()))), errors='raise')
                    datetime_cols.append(col)
                except (ValueError, TypeError):
                    continue
        return datetime_cols

    def get_summary_stats(self) -> Dict[str, Any]:
        summary = {
            'basic_info': {
                'rows': len(self.df),
                'columns': len(self.df.columns),
                'missing_values': int(self.df.isnull().sum().sum())
            },
            'numeric_summary': pd.DataFrame(),
        }
        if self.numeric_columns:
            summary['numeric_summary'] = self.df[self.numeric_columns].describe().transpose()
        return summary

    def get_insights(self) -> List[Dict[str, str]]:
        insights = []
        rows, cols = self.df.shape
        insights.append({
            'type': 'Overview',
            'message': f"The dataset contains {rows:,} rows and {cols} columns."
        })

        total_cells = np.prod(self.df.shape)
        missing_count = self.df.isnull().sum().sum()
        if missing_count > 0:
            missing_pct = (missing_count / total_cells) * 100
            insights.append({
                'type': 'Data Quality Issue',
                'message': f"Found {missing_count:,} missing values ({missing_pct:.2f}% of total data)."
            })
        else:
            insights.append({
                'type': 'Data Quality',
                'message': "No missing values were detected."
            })

        if len(self.numeric_columns) >= 2:
            corr_matrix = self.df[self.numeric_columns].corr().abs()
            sol = corr_matrix.unstack()
            so = sol[sol.between(0.8, 1, inclusive='neither')]
            if not so.empty:
                insights.append({
                    'type': 'Correlation',
                    'message': f"Found {len(so)//2} pair(s) of highly correlated numeric columns (correlation > 0.8)."
                })
        
        if self.categorical_columns:
            high_cardinality_cols = [
                col for col in self.categorical_columns 
                if self.df[col].nunique() > 50 and self.df[col].nunique() / rows > 0.5
            ]
            if high_cardinality_cols:
                insights.append({
                    'type': 'Data Cardinality',
                    'message': f"High cardinality detected in columns: {', '.join(high_cardinality_cols)}."
                })
        return insights

    def generate_report(self) -> str:
        report = ["=" * 50, "DataLoom - Data Analysis Report", "=" * 50, ""]
        summary = self.get_summary_stats()

        report.append("1. DATASET OVERVIEW")
        report.append("-" * 20)
        report.append(f"Rows: {summary['basic_info']['rows']:,}")
        report.append(f"Columns: {summary['basic_info']['columns']}")
        report.append(f"Missing Values: {summary['basic_info']['missing_values']:,}")
        report.append("")
        
        if not summary['numeric_summary'].empty:
            report.append("2. NUMERIC COLUMNS SUMMARY")
            report.append("-" * 20)
            report.append(summary['numeric_summary'].to_string())
            report.append("")

        insights = self.get_insights()
        if insights:
            report.append("3. KEY INSIGHTS")
            report.append("-" * 20)
            for insight in insights:
                report.append(f"- {insight['type']}: {insight['message']}")
            report.append("")

        report.append("=" * 50)
        return "\n".join(report)