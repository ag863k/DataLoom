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
                    values = self.df[col].dropna()
                    if len(values) == 0:
                        continue
                    converted = pd.to_datetime(values, format='mixed', errors='coerce')
                    if converted.notna().mean() >= 0.9:
                        datetime_cols.append(col)
                except (ValueError, TypeError, OverflowError):
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

        if self.datetime_columns:
            date_ranges = []
            for column in self.datetime_columns:
                dates = pd.to_datetime(self.df[column], errors='coerce').dropna()
                if not dates.empty:
                    date_ranges.append(
                        f"{column}: {dates.min().strftime('%d %b %Y')} to {dates.max().strftime('%d %b %Y')}"
                    )
            if date_ranges:
                insights.append({
                    'type': 'Date Coverage',
                    'message': '; '.join(date_ranges) + '.'
                })

        if len(self.numeric_columns) >= 2:
            corr_matrix = self.df[self.numeric_columns].corr().abs()
            upper_triangle = np.triu(np.ones(corr_matrix.shape, dtype=bool), k=1)
            strong_pairs = corr_matrix.where(upper_triangle).stack()
            if not strong_pairs.empty:
                strongest_pair = strong_pairs.idxmax()
                insights.append({
                    'type': 'Correlation',
                    'message': f"Found {len(strong_pairs)} highly correlated numeric pair(s). Strongest: {strongest_pair[0]} and {strongest_pair[1]} ({strong_pairs.max():.2f})."
                })

        categorical_columns = [
            column for column in self.categorical_columns
            if column not in self.datetime_columns
        ]
        if categorical_columns:
            high_cardinality_cols = [
                col for col in categorical_columns
                if self.df[col].nunique() > 50 and self.df[col].nunique() / rows > 0.5
            ]
            if high_cardinality_cols:
                insights.append({
                    'type': 'Data Cardinality',
                    'message': f"High cardinality detected in columns: {', '.join(high_cardinality_cols)}."
                })

            largest_category = max(categorical_columns, key=lambda col: self.df[col].nunique())
            insights.append({
                'type': 'Category Summary',
                'message': f"{largest_category} contains {self.df[largest_category].nunique()} distinct value(s)."
            })

        if self.numeric_columns:
            spread_column = max(self.numeric_columns, key=lambda col: self.df[col].std(skipna=True) or 0)
            insights.append({
                'type': 'Numeric Summary',
                'message': f"{spread_column} has the widest variation, from {self.df[spread_column].min():,.2f} to {self.df[spread_column].max():,.2f}."
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