from flask import Blueprint, render_template, flash, redirect, url_for, request, make_response
from flask_login import login_required
from . import db
from app.models import File, User
from datetime import datetime
import pdfkit
import pandas as pd
import json
import numpy as np
import os

path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports', methods=['GET'])
@login_required
def reports():
    search_query = request.args.get('search', '').strip()
    date_query = request.args.get('date', '').strip()

    query = db.session.query(File.id, File.filename, User.name, File.created_at).join(User, File.user_id == User.id)

    if search_query:
        query = query.filter(File.filename.ilike(f"%{search_query}%"))
    if date_query:
        try:
            date_obj = datetime.strptime(date_query, '%Y-%m-%d').date()
            query = query.filter(db.func.date(File.created_at) == date_obj)
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")

    datasets = query.all()

    return render_template('reports.html', datasets=datasets, search_query=search_query, date_query=date_query)


@reports_bp.route('/generate_pdf/<int:id>', methods=['GET'])
def generate_pdf(id):
    query = db.session.query(File.id, File.filename, User.name, File.created_at).join(User, File.user_id == User.id).filter(File.id == id).first()
    
    file_path = os.path.join(UPLOAD_FOLDER, query.filename)
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
    
    html = render_template('pdf_template.html', dataset=query, dataset_summary=dataset_summary)
    pdf = pdfkit.from_string(html, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=output.pdf'
    return response