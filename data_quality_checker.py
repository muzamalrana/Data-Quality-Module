import pandas as pd
import numpy as np
import re

class DataQualityChecker:
    def __init__(self, df: pd.DataFrame, date_column: str = None):
        self.df = df.copy()
        self.date_column = date_column

    def run_all_checks(self):
        results = {
            "column_summary": self._column_summary(),
            "nulls": self._null_counts(),
            "outliers": self._outlier_summary(),
            "duplicates": self._duplicate_summary(),
            "mixed_types": self._mixed_type_check(),
            "outliers_by_date": self._outliers_by_date() if self.date_column else pd.DataFrame(),
            "placeholder_counts": self._placeholder_counts(),
            "placeholder_counts_by_date": self._placeholder_counts_by_date() if self.date_column else pd.DataFrame()
    
        }
        if self.date_column:
            results["nulls_by_date"], results["empty_strings_by_date"] = self._nulls_and_empty_strings_by_date()
        else:
            results["nulls_by_date"] = pd.DataFrame()
            results["empty_strings_by_date"] = pd.DataFrame()

        results["null_rows"] = self.null_rows  # dict of DataFrames
        results["outlier_rows"] = self.outlier_rows  # dict of DataFrames
        results["placeholder_rows"] = self.placeholder_rows  # dict of DataFrames
        
        return results

    def _column_summary(self):
        summary = []
        for col in self.df.columns:
            summary.append({
                "column": col,
                "dtype": str(self.df[col].dtype),
                "non_null_count": self.df[col].notnull().sum(),
                "null_count": self.df[col].isnull().sum(),
                "null_percentage": self.df[col].isnull().sum() / len(self.df) * 100,
                "unique_values": self.df[col].nunique(),
                "sample_values": self.df[col].dropna().unique()[:3].tolist()
            })
        return pd.DataFrame(summary)

    def _null_counts(self):
        nulls = self.df.isnull().sum().reset_index()
        nulls.columns = ['column', 'null_count']
        nulls['null_percentage'] = (nulls['null_count'] / len(self.df)) * 100

        self.null_rows = {col: self.df[self.df[col].isnull()].copy()
                          for col in self.df.columns if self.df[col].isnull().any()}
        return nulls

    def _outlier_summary(self):
        outlier_data = []
        self.outlier_rows = {}  # Reset
        
        for col in self.df.select_dtypes(include=[np.number]).columns:
            q1 = self.df[col].quantile(0.25)
            q3 = self.df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            outliers = self.df[(self.df[col] < lower) | (self.df[col] > upper)]
            self.outlier_rows[col] = outliers.copy()

            outlier_data.append({
                'column': col,
                'outlier_count': len(outliers),
                'total_count': len(self.df),
                'outlier_percentage': (len(outliers) / len(self.df)) * 100
            })
        return pd.DataFrame(outlier_data)

    def _duplicate_summary(self):
        total_rows = len(self.df)
        duplicate_rows = self.df.duplicated().sum()
        return pd.DataFrame([{
            'total_rows': total_rows,
            'duplicate_rows': duplicate_rows,
            'duplicate_percentage': (duplicate_rows / total_rows) * 100
        }])

    def _mixed_type_check(self):
        result = []
        for col in self.df.columns:
            types = self.df[col].dropna().apply(type).value_counts()
            if len(types) > 1:
                result.append({
                    "column": col,
                    "type_counts": dict(types)
                })
        return pd.DataFrame(result)

    def _nulls_and_empty_strings_by_date(self):
        df = self.df.copy()
        df[self.date_column] = pd.to_datetime(df[self.date_column], errors='coerce')
        df = df.dropna(subset=[self.date_column])
        df['date_only'] = df[self.date_column].dt.date

        melted = df.melt(id_vars=['date_only'], var_name='column', value_name='value')
        total_per_date = df.groupby('date_only').size().reset_index(name='total_count')

        nulls = melted[melted['value'].isnull()]
        null_counts = nulls.groupby(['date_only', 'column']).size().reset_index(name='null_count')
        null_counts = null_counts.merge(total_per_date, on='date_only', how='left')
        null_counts['null_percentage'] = (null_counts['null_count'] / null_counts['total_count']) * 100
        null_counts.drop(columns=['total_count'], inplace=True)

        str_cols = df.select_dtypes(include=['object']).columns.tolist()
        melted_str = melted[melted['column'].isin(str_cols)].copy()
        empty_strs = melted_str[melted_str['value'].astype(str).str.strip() == '']
        empty_counts = empty_strs.groupby(['date_only', 'column']).size().reset_index(name='empty_string_count')
        empty_counts = empty_counts.merge(total_per_date, on='date_only', how='left')
        empty_counts['empty_string_percentage'] = (empty_counts['empty_string_count'] / empty_counts['total_count']) * 100
        empty_counts.drop(columns=['total_count'], inplace=True)

        return null_counts, empty_counts

    def _outliers_by_date(self):
        if not self.date_column:
            return pd.DataFrame()
        df = self.df.copy()
        df[self.date_column] = pd.to_datetime(df[self.date_column], errors='coerce')
        df = df.dropna(subset=[self.date_column])
        df['date_only'] = df[self.date_column].dt.date

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        result = []

        for col in numeric_cols:
            for date, group in df.groupby('date_only'):
                if group[col].dropna().shape[0] < 5:
                    continue

                q1 = group[col].quantile(0.25)
                q3 = group[col].quantile(0.75)
                iqr = q3 - q1
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr

                outlier_count = group[(group[col] < lower) | (group[col] > upper)].shape[0]
                total_count = group[col].notnull().sum()

                result.append({
                    "date_only": date,
                    "column": col,
                    "outlier_count": outlier_count,
                    "total_count": total_count,
                    "outlier_percentage": (outlier_count / total_count) * 100 if total_count > 0 else 0
                })

        return pd.DataFrame(result)



    def _placeholder_counts(self):
        placeholders = [
            r"other", r"others", r"unknown", r"undefined", r"not available", r"not known",
            r"not specified", r"none", r"missing", r"n/?a", r"null", r"tbd", r"default",
            r"\?", r"--", r"_", r"no data", r"empty", r"select", r"choose"
        ]
        pattern = re.compile(r"^(" + "|".join(placeholders) + r")$", re.IGNORECASE)
    
        self.placeholder_rows = {}
        data = []
    
        obj_cols = self.df.select_dtypes(include=['object']).columns
        total_rows = len(self.df)
    
        for col in obj_cols:
            full_series = self.df[col]  # Includes nulls
    
            # Apply pattern to only non-null values
            stripped = full_series.dropna().astype(str).str.strip()
            placeholder_mask = stripped.str.match(pattern)
            placeholder_count = placeholder_mask.sum()
    
            # Mask for original df to extract rows (including nulls, but won't match)
            final_mask = full_series.astype(str).str.strip().str.match(pattern)
            self.placeholder_rows[col] = self.df[final_mask].copy()
    
            percentage = (placeholder_count / total_rows) * 100 if total_rows > 0 else 0
    
            data.append({
                "column": col,
                "placeholder_count": placeholder_count,
                "total_rows": total_rows,
                "placeholder_percentage": percentage
            })
    
        return pd.DataFrame(data)
    

    def _placeholder_counts_by_date(self):
        placeholders = [
            r"other", r"others", r"unknown", r"undefined", r"not available", r"not known",
            r"not specified", r"none", r"missing", r"n/?a", r"null", r"tbd", r"default",
            r"\?", r"--", r"_", r"no data", r"empty", r"select", r"choose"
        ]
        pattern = re.compile(r"^(" + "|".join(placeholders) + r")$", re.IGNORECASE)
    
        df = self.df.copy()
        df[self.date_column] = pd.to_datetime(df[self.date_column], errors='coerce')
        df = df.dropna(subset=[self.date_column])
        df['date_only'] = df[self.date_column].dt.date
    
        obj_cols = df.select_dtypes(include=['object']).columns
    
        melted = df.melt(id_vars=['date_only'], value_vars=obj_cols, var_name='column', value_name='value')
    
        # Total rows per date and column (including nulls)
        total_per_date = melted.groupby(['date_only', 'column']).size().reset_index(name='total_rows')
    
        # Filter non-null values for matching
        melted_non_null = melted[melted['value'].notnull()].copy()
        melted_non_null['value_stripped'] = melted_non_null['value'].astype(str).str.strip()
    
        placeholder_mask = melted_non_null['value_stripped'].str.match(pattern)
        placeholder_df = melted_non_null[placeholder_mask]
    
        # Count placeholders by date and column
        placeholder_counts = placeholder_df.groupby(['date_only', 'column']).size().reset_index(name='placeholder_count')
    
        # Merge with total rows to calculate percentage
        merged = placeholder_counts.merge(total_per_date, on=['date_only', 'column'], how='left')
        merged['placeholder_percentage'] = (merged['placeholder_count'] / merged['total_rows']) * 100
    
        return merged
