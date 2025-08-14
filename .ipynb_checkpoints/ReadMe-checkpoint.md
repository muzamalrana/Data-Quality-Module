# Data Quality Module

A modular Python framework for performing data quality checks across various data sources, including databases, APIs, and flat files.  
Designed to be extendable, easy to integrate, and suitable for both automated pipelines and standalone runs.

---

## 📌 Features
- **Multiple Data Sources**: Supports files, APIs, and databases.
- **Customizable Checks**: Easily add or modify data quality rules.
- **Logging**: Detailed logs for debugging and auditing.
- **Results Storage**: Saves data quality results for review.
- **Modular Structure**: Clear separation of loaders, handlers, and utilities.

---

## 📂 Project Structure
DQ-repo/
├── api_handlers/ # API connection & data retrieval
├── db_handlers/ # Database connection & queries
├── file_handlers/ # File read/write utilities
├── utils/ # Helper functions
├── dq_results/ # Data quality results storage
├── logs/ # Log files
├── data_loader.py # Data loading entry point
├── data_quality_checker.py # Main DQ checks
├── requirements.txt # Python dependencies
└── README.md # Project documentation