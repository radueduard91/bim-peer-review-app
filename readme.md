# BIM Data Visualization App

This application replicates the logic from Power Query transformations in a Python-based web interface. It allows users to select local VP Excel files and SharePoint files to process and visualize relationships between entities, attributes, and systems.

## Features

- **File Selection:** Browse and select local VP Excel and SharePoint Excel files
- **Sheet Selection:** Choose which sheet to load from the Central Document
- **Data Visualization:** View entity relationships in a network diagram
- **Quality Assurance:** Check for system mismatches, missing relationships, and view entity statistics

## Project Structure

```
bim-testing-app/
├── app.py                # Central entry point (loads modules, runs Dash app)
├── etl/
│   ├── load_local.py      # Code to load and process local files
│   ├── transformations.py # Transformations applied to the loaded data
├── dash_components/
│   ├── file_selector.py   # Dash component for browsing and selecting local files
│   ├── sheet_selector.py  # Dash component for choosing which sheet to load
│   ├── data_diagram.py    # Dash visualization of the processed data
│   ├── qa_checks.py       # Dash visualization for QA checks
├── assets/                # Static files for Dash (CSS, logos, etc.)
├── requirements.txt       # List of Python dependencies
└── README.md              # Instructions for setup
```

## Installation

1. Clone this repository to your local machine:
   ```
   git clone <repository-url> C:\Users\R40008\Asset Model Server\python\bim-testing-app
   ```

2. Navigate to the project directory:
   ```
   cd C:\Users\R40008\Asset Model Server\python\bim-testing-app
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8050/
   ```

3. In the application:
   - Select the VP Excel file
   - Select the downloaded SharePoint Central Document file
   - Choose the sheet to load from the Central Document
   - Click "Load Data" to process the files
   - Explore the visualizations and QA checks

## Data Files

### VP Excel File
The application expects the VP Excel file to have the following sheets:
- Entity: Contains information about data entities
- Column: Contains information about entity attributes
- Foreign Key: Contains relationship information between entities

### Central Document File
The application expects the Central Document Excel file to have a "Linear" sheet containing system information about objects and attributes.

## Notes for Development

- File browsing: The current implementation uses file paths entered in text boxes. For a production environment, consider implementing a proper file browser using libraries like tkinter or PyQt.
- Error handling: Additional error handling and validation can be added to improve robustness.
- Performance: For large files, consider implementing progress indicators and optimization techniques.
