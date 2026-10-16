import pandas as pd
import numpy as np
from typing import Dict, Any, List


class DataAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
        self.categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.datetime_columns = self._detect_datetime_columns()
        self.dataset_type = self._detect_dataset_type()
        self.key_columns = self._identify_key_columns()

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
                except Exception:
                    continue
        return datetime_cols

    def _detect_dataset_type(self) -> str:
        col_names_lower = [col.lower() for col in self.df.columns]
        
        sales_keywords = ['sale', 'revenue', 'price', 'product', 'order', 'quantity', 'discount']
        customer_keywords = ['customer', 'client', 'user', 'account', 'contact', 'email']
        financial_keywords = ['expense', 'income', 'transaction', 'balance', 'payment', 'credit', 'debit']
        hr_keywords = ['employee', 'salary', 'department', 'hire', 'position', 'attendance']
        inventory_keywords = ['stock', 'inventory', 'warehouse', 'supplier', 'sku', 'reorder']
        marketing_keywords = ['campaign', 'ad', 'click', 'impression', 'conversion', 'lead']
        
        scores = {
            'sales': sum(1 for kw in sales_keywords if any(kw in col for col in col_names_lower)),
            'customer': sum(1 for kw in customer_keywords if any(kw in col for col in col_names_lower)),
            'financial': sum(1 for kw in financial_keywords if any(kw in col for col in col_names_lower)),
            'hr': sum(1 for kw in hr_keywords if any(kw in col for col in col_names_lower)),
            'inventory': sum(1 for kw in inventory_keywords if any(kw in col for col in col_names_lower)),
            'marketing': sum(1 for kw in marketing_keywords if any(kw in col for col in col_names_lower))
        }
        
        if self.datetime_columns:
            scores['timeseries'] = len(self.datetime_columns) * 2
        
        detected_type = max(scores, key=scores.get) if max(scores.values()) > 0 else 'general'
        return detected_type if scores[detected_type] >= 2 else 'general'

    def _identify_key_columns(self) -> Dict[str, List[str]]:
        keys = {
            'id_columns': [],
            'amount_columns': [],
            'date_columns': self.datetime_columns.copy(),
            'text_columns': []
        }
        
        for col in self.df.columns:
            col_lower = col.lower()
            unique_ratio = self.df[col].nunique() / len(self.df) if len(self.df) > 0 else 0
            
            if col in self.numeric_columns:
                if 'id' in col_lower or unique_ratio > 0.95:
                    keys['id_columns'].append(col)
                elif any(kw in col_lower for kw in ['price', 'amount', 'cost', 'revenue', 'salary', 'expense', 'total']):
                    keys['amount_columns'].append(col)
            elif col in self.categorical_columns:
                if 'id' in col_lower and unique_ratio > 0.9:
                    keys['id_columns'].append(col)
                elif len(str(self.df[col].iloc[0] if len(self.df) > 0 else '')) > 50:
                    keys['text_columns'].append(col)
        
        return keys

    def get_summary_stats(self) -> Dict[str, Any]:
        summary = {
            'basic_info': {
                'rows': len(self.df),
                'columns': len(self.df.columns),
                'missing_values': int(self.df.isnull().sum().sum()),
                'dataset_type': self.dataset_type.title()
            },
            'numeric_summary': pd.DataFrame(),
        }
        if self.numeric_columns:
            numeric_cols = [col for col in self.numeric_columns if col not in self.key_columns['id_columns']]
            if numeric_cols:
                summary['numeric_summary'] = self.df[numeric_cols].describe().transpose()
        return summary

    def get_insights(self) -> List[Dict[str, str]]:
        insights = []
        rows, cols = self.df.shape
        
        insights.append({
            'type': 'Dataset Type',
            'message': f"{self.dataset_type.title()} dataset with {rows:,} rows and {cols} columns"
        })

        total_cells = np.prod(self.df.shape)
        missing_count = self.df.isnull().sum().sum()
        if missing_count > 0:
            missing_pct = (missing_count / total_cells) * 100
            insights.append({
                'type': 'Data Quality',
                'message': f"{missing_count:,} missing values ({missing_pct:.1f}% of data)"
            })

        if self.datetime_columns:
            for col in self.datetime_columns[:2]:
                try:
                    dates = pd.to_datetime(self.df[col], errors='coerce').dropna()
                    if not dates.empty:
                        span = (dates.max() - dates.min()).days
                        insights.append({
                            'type': 'Time Range',
                            'message': f"{col}: {dates.min().strftime('%b %Y')} to {dates.max().strftime('%b %Y')} ({span} days)"
                        })
                except Exception:
                    continue

        if self.key_columns['amount_columns']:
            for col in self.key_columns['amount_columns'][:2]:
                total = self.df[col].sum()
                mean = self.df[col].mean()
                insights.append({
                    'type': 'Financial Metric',
                    'message': f"{col}: Total ${total:,.2f}, Average ${mean:,.2f}"
                })

        numeric_cols = [col for col in self.numeric_columns if col not in self.key_columns['id_columns']]
        if len(numeric_cols) >= 2:
            corr_matrix = self.df[numeric_cols].corr().abs()
            upper_triangle = np.triu(np.ones(corr_matrix.shape, dtype=bool), k=1)
            strong_pairs = corr_matrix.where(upper_triangle).stack()
            strong_pairs = strong_pairs[strong_pairs > 0.7]
            if not strong_pairs.empty:
                strongest = strong_pairs.idxmax()
                insights.append({
                    'type': 'Strong Correlation',
                    'message': f"{strongest[0]} and {strongest[1]} are highly correlated ({strong_pairs.max():.2f})"
                })

        categorical_cols = [col for col in self.categorical_columns if col not in self.datetime_columns]
        for col in categorical_cols[:3]:
            unique_count = self.df[col].nunique()
            if unique_count <= 10:
                top_value = self.df[col].value_counts().index[0]
                top_count = self.df[col].value_counts().iloc[0]
                insights.append({
                    'type': 'Category Distribution',
                    'message': f"{col}: {unique_count} categories, most common is '{top_value}' ({top_count} occurrences)"
                })
            elif unique_count > 50:
                insights.append({
                    'type': 'High Cardinality',
                    'message': f"{col} has {unique_count} unique values (high diversity)"
                })

        if len(self.df) > 1:
            duplicates = self.df.duplicated().sum()
            if duplicates > 0:
                insights.append({
                    'type': 'Data Quality',
                    'message': f"{duplicates} duplicate rows found ({(duplicates/len(self.df)*100):.1f}%)"
                })

        return insights

    def generate_report(self) -> str:
        report = ["=" * 60, "DataLoom Analysis Report", "=" * 60, ""]
        summary = self.get_summary_stats()

        report.append("DATASET OVERVIEW")
        report.append("-" * 60)
        report.append(f"Type: {summary['basic_info']['dataset_type']}")
        report.append(f"Rows: {summary['basic_info']['rows']:,}")
        report.append(f"Columns: {summary['basic_info']['columns']}")
        report.append(f"Missing Values: {summary['basic_info']['missing_values']:,}")
        report.append("")
        
        if self.datetime_columns:
            report.append("TIME-SERIES COLUMNS")
            report.append("-" * 60)
            for col in self.datetime_columns:
                report.append(f"- {col}")
            report.append("")
        
        if self.key_columns['amount_columns']:
            report.append("FINANCIAL/AMOUNT COLUMNS")
            report.append("-" * 60)
            for col in self.key_columns['amount_columns']:
                report.append(f"- {col}")
            report.append("")
        
        if not summary['numeric_summary'].empty:
            report.append("NUMERIC STATISTICS")
            report.append("-" * 60)
            report.append(summary['numeric_summary'].to_string())
            report.append("")

        insights = self.get_insights()
        if insights:
            report.append("KEY INSIGHTS")
            report.append("-" * 60)
            for insight in insights:
                report.append(f"[{insight['type']}] {insight['message']}")
            report.append("")

        report.append("=" * 60)
        return "\n".join(report)
