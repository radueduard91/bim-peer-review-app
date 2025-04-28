import os
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import pandas as pd

# Import modules
from etl.load_local import get_data_folders
from dash_components.file_selector import create_file_selector

# Set up the application
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="BIM Data Visualization App"
)

# Define the layout
app.layout = html.Div([
    html.H1("BIM Data Visualization App"),
    html.Div([
        html.H2("Data Selection"),
        html.Div([
            # VP File Selector
            create_file_selector(
                id_prefix="vp-file",
                label="Select VP Excel File:",
                default_path=os.path.join(get_data_folders()["data_folder"], "vp excel export - clean.xlsx")
            ),
            
            # Central Document File Selector
            create_file_selector(
                id_prefix="central-doc",
                label="Select Central Document Excel File:",
                default_path=""
            ),
            
            # Sheet Selector
            html.Div([
                html.Label("Select Sheet (for Central Document only):"),
                dcc.Dropdown(
                    id="central-doc-sheet-dropdown",
                    options=[
                        {'label': 'Linear (default)', 'value': 'Linear'}
                    ],
                    value='Linear',
                    clearable=False
                ),
                html.Button(
                    "Get Sheets", 
                    id="central-doc-sheet-get-sheets",
                    style={"margin": "10px 0"}
                ),
                html.Div(id="central-doc-sheet-output")
            ], className="sheet-selector"),
            
            # Load Button
            html.Button("Load Data", id="load-data-button", n_clicks=0),
            html.Div(id="loading-output")
        ], className="file-selectors"),
    ]),
    html.Div([
        html.H2("Data Visualization"),
        html.Div(id="data-view", children=[
            html.Div(id="data-diagram-container"),
            html.Div(id="qa-checks-container")
        ])
    ]),
    # Store components for holding the data
    dcc.Store(id="vp-entities-store"),
    dcc.Store(id="vp-attributes-store"),
    dcc.Store(id="vp-relationships-store"),
    dcc.Store(id="central-doc-object-labels-store"),
    dcc.Store(id="central-doc-attribute-labels-store")
])

# Callback for sheet selector
@app.callback(
    [Output("central-doc-sheet-dropdown", "options"),
     Output("central-doc-sheet-output", "children")],
    [Input("central-doc-sheet-get-sheets", "n_clicks")],
    [State("central-doc-path", "value")]
)
def update_sheet_dropdown(n_clicks, file_path):
    if n_clicks is None or n_clicks == 0:
        return [{'label': 'Linear (default)', 'value': 'Linear'}], ""
    
    if not file_path:
        return [{'label': 'Linear (default)', 'value': 'Linear'}], "Please select a file first"
    
    try:
        # Read Excel file to get sheet names
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        
        # Create dropdown options
        options = [{'label': name, 'value': name} for name in sheet_names]
        
        # Set default to "Linear" if it exists
        if "Linear" in sheet_names:
            return options, f"Found {len(sheet_names)} sheets in the file"
        else:
            return options, f"Found {len(sheet_names)} sheets in the file (Note: 'Linear' sheet not found)"
            
    except Exception as e:
        return [{'label': 'Linear (default)', 'value': 'Linear'}], f"Error loading sheets: {str(e)}"

# Callback for file selection outputs
@app.callback(
    Output("vp-file-output", "children"),
    [Input("vp-file-upload", "contents")],
    [State("vp-file-upload", "filename"), 
     State("vp-file-path", "value")]
)
def update_vp_file_output(contents, filename, current_path):
    if contents is not None:
        return f"Selected file: {filename}"
    elif current_path:
        return f"Selected file: {os.path.basename(current_path)}"
    return ""

@app.callback(
    Output("central-doc-output", "children"),
    [Input("central-doc-upload", "contents")],
    [State("central-doc-upload", "filename"),
     State("central-doc-path", "value")]
)
def update_central_doc_output(contents, filename, current_path):
    if contents is not None:
        return f"Selected file: {filename}"
    elif current_path:
        return f"Selected file: {os.path.basename(current_path)}"
    return ""

# Main callback for data loading and processing
@app.callback(
    [Output("loading-output", "children"),
     Output("vp-entities-store", "data"),
     Output("vp-attributes-store", "data"),
     Output("vp-relationships-store", "data"),
     Output("central-doc-object-labels-store", "data"),
     Output("central-doc-attribute-labels-store", "data"),
     Output("data-diagram-container", "children"),
     Output("qa-checks-container", "children")],
    [Input("load-data-button", "n_clicks")],
    [State("vp-file-path", "value"),
     State("central-doc-path", "value"),
     State("central-doc-sheet-dropdown", "value")]
)
def load_and_process_data(n_clicks, vp_file_path, central_doc_path, sheet_name):
    if n_clicks == 0:
        return "Please select files and click 'Load Data'", None, None, None, None, None, None, None
    
    if not vp_file_path or not central_doc_path:
        return "Please select both files", None, None, None, None, None, None, None
    
    if not sheet_name:
        sheet_name = "Linear"  # Default sheet name if none selected
    
    try:
        # Import these inside the callback to avoid circular imports
        from etl.load_local import load_vp_files, load_central_doc
        from etl.transformations import process_data
        from dash_components.data_diagram import create_data_diagram
        from dash_components.qa_checks import create_qa_checks
        
        # Load data from files
        vp_entities, vp_attributes, vp_relationships = load_vp_files(vp_file_path)
        central_doc_object_labels, central_doc_attribute_labels = load_central_doc(
            central_doc_path, sheet_name)
        
        # Process data (apply Power Query transformations)
        results = process_data(
            vp_entities, 
            vp_attributes, 
            vp_relationships, 
            central_doc_object_labels, 
            central_doc_attribute_labels
        )
        
        # Create visualizations
        diagram = create_data_diagram(results)
        qa_checks = create_qa_checks(results)
        
        return (
            "Data loaded successfully", 
            results["vp_entities"].to_dict('records'), 
            results["vp_attributes"].to_dict('records'),
            results["vp_relationships"].to_dict('records'),
            results["central_doc_object_labels"].to_dict('records'),
            results["central_doc_attribute_labels"].to_dict('records'),
            diagram,
            qa_checks
        )
    except Exception as e:
        return f"Error: {str(e)}", None, None, None, None, None, None, None

if __name__ == "__main__":
    app.run(debug=True)