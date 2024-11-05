from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from flask_login import login_required
import pandas as pd
import json
import numpy as np
import uuid
import os
from io import StringIO
from . import db
from app.models import File
from datetime import datetime


dashboard_bp = Blueprint('dashboard', __name__)

#UPLOAD_FOLDER = '/app/static/uploads'
#os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')


@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.csv'):
            #df = pd.read_csv(file)
            #save_df_to_session(df)
            filename = f"{uuid.uuid4()}.csv"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            file_size_bytes = os.path.getsize(file_path)
            # Convert to KB or MB if necessary
            file_size_kb = file_size_bytes / 1024
            file_size_mb = file_size_kb / 1024
            
            new_file = File(
                user_id=session['userid'],
                filename=filename,
                size=file_size_mb,
                created_at=datetime.now()
            )

            db.session.add(new_file)
            db.session.commit()
            
            
            session['dataset_path'] = file_path
            df = pd.read_csv(file_path)
            
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
            
            #print(dataset_summary)
            return render_template('results.html', dataset_summary=dataset_summary)

        else:
            flash('Please upload a valid CSV file.')
            return redirect(url_for('dashboard.dashboard'))
    
    dataset_summary = {}
    return render_template('dashboard.html', dataset_summary=dataset_summary)


@dashboard_bp.route('/generate_pie_chart', methods=['POST'])
@login_required
def generate_pie_chart():
    try:
        data = request.get_json()
        selected_column = data.get('selected_column')
        
        if not selected_column:
            return jsonify({"error": "No column selected. Please choose a column for the pie chart."}), 400

        df = pd.read_csv(session['dataset_path'])
        if df is None:
            return jsonify({"error": "No dataset found. Please upload the dataset again."}), 404

        if selected_column not in df.columns:
            return jsonify({"error": f'Column "{selected_column}" not found in the uploaded dataset.'}), 400

        value_counts = df[selected_column].value_counts()
        labels = value_counts.index.tolist()
        values = value_counts.values.tolist()

        print(values)
        return jsonify({"labels": labels, "values": values})

    except Exception as e:
        return jsonify({"error": "An error occurred while generating the pie chart.", "details": str(e)}), 500


@dashboard_bp.route('/generate_bar_chart', methods=['POST'])
@login_required
def generate_bar_chart():
    try:
        data = request.get_json()
        selected_column = data.get('selected_column')
        
        if not selected_column:
            return jsonify({"error": "No column selected. Please choose a column for the bar chart."}), 400

        df = pd.read_csv(session['dataset_path'])
        if df is None:
            return jsonify({"error": "No dataset found. Please upload the dataset again."}), 404

        if selected_column not in df.columns:
            return jsonify({"error": f'Column "{selected_column}" not found in the uploaded dataset.'}), 400

        # Generate bar chart data
        value_counts = df[selected_column].value_counts()
        labels = value_counts.index.tolist()
        values = value_counts.values.tolist()

        return jsonify({"labels": labels, "values": values})

    except Exception as e:
        return jsonify({"error": "An error occurred while generating the bar chart.", "details": str(e)}), 500
