Data Quality Module

Overview:
The Data Quality Module is a Python-based tool designed to analyze, monitor, and visualize the quality of datasets. It provides features like data profiling, missing value analysis, duplicate detection, and interactive dashboards using Dash & Plotly.

Table of Contents

About

Installation

Usage

Features

Git Operations

License

About

This module helps data engineers and analysts to:

Quickly assess the quality of any dataset.

Identify missing or inconsistent data.

Visualize statistics and trends over time.

Export reports or dashboards for stakeholders.

Installation
# Clone the repository
git clone https://github.com/muzamalrana/Data-Quality-Module.git

# Navigate into project folder
cd Data-Quality-Module

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install required dependencies
pip install -r requirements.txt

Usage

Run the Dash Web Application:

python app.py


Load your dataset in CSV format.

Use the interactive dashboard to analyze and visualize data quality metrics.

Export results if needed for reporting.

Features

Data profiling (missing values, duplicates, column statistics)

Time-based quality analysis

Interactive graphs with Plotly

Automated reports in CSV/HTML

Configurable for multiple datasets
