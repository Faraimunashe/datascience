from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
import pandas as pd
import json
import numpy as np


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file)

            numeric_df = df.select_dtypes(include=['number'])

            metadata = {
                "Number of Rows": int(df.shape[0]),
                "Number of Columns": int(df.shape[1]),
                "Column Names and Types": {col: str(dtype) for col, dtype in df.dtypes.items()}
            }

            summary_stats = numeric_df.describe().applymap(
                lambda x: x.item() if isinstance(x, np.generic) else x
            ).to_dict()

            missing_data = {
                "Total Missing": {col: int(missing) for col, missing in df.isnull().sum().items()},
                "Percentage Missing": {col: round(percent, 2) for col, percent in (df.isnull().mean() * 100).items()}
            }

            unique_values = {col: int(df[col].nunique()) for col in df.columns}
            most_common_values = {col: df[col].mode()[0] if not df[col].mode().empty else None for col in df.columns}

            correlation_matrix = numeric_df.corr().round(2).applymap(
                lambda x: x.item() if isinstance(x, np.generic) else x
            ).to_dict()

            distribution_stats = {
                "Skewness": {col: round(skew, 2) for col, skew in numeric_df.skew().items()},
                "Kurtosis": {col: round(kurt, 2) for col, kurt in numeric_df.kurt().items()}
            }

            dataset_summary = {
                "Metadata": metadata,
                "Summary Statistics": summary_stats,
                "Missing Data": missing_data,
                "Unique Values": unique_values,
                "Most Common Values": most_common_values,
                "Correlation Matrix": correlation_matrix,
                "Distribution Statistics": distribution_stats
            }
            
            print(dataset_summary)
            return render_template('results.html', dataset_summary=dataset_summary)

        else:
            flash('Please upload a valid CSV file.')
            return redirect(url_for('dashboard.dashboard'))
    
    dataset_summary = {}
    return render_template('dashboard.html', dataset_summary=dataset_summary)
