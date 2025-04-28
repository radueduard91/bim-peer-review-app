import pandas as pd
from dash import html, dcc
from dash.dependencies import Input, Output, State

def create_sheet_selector(id_prefix):
    """
    Create a sheet selector dropdown for Excel files.
    
    Args:
        id_prefix (str): Prefix for the component IDs
        
    Returns:
        html.Div: The sheet selector component
    """
    return html.Div([
        html.Label("Select Sheet (for Central Document only):"),
        dcc.Dropdown(
            id=f"{id_prefix}-dropdown",
            options=[
                {'label': 'Linear (default)', 'value': 'Linear'}
            ],
            value='Linear',  # Default value
            clearable=False
        ),
        html.Button(
            "Get Sheets", 
            id=f"{id_prefix}-get-sheets",
            style={"margin": "10px 0"}
        ),
        html.Div(id=f"{id_prefix}-output")
    ], className="sheet-selector")

def register_sheet_selector_callbacks(app):
    """
    Register callbacks for the sheet selector component.
    
    Args:
        app: The Dash app
    """
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
    
    @app.callback(
        Output("central-doc-sheet-dropdown", "value"),
        [Input("central-doc-sheet-dropdown", "options")],
        [State("central-doc-sheet-dropdown", "value")]
    )
    def set_default_sheet(options, current_value):
        # If "Linear" is available, select it as default when options change
        if options and any(option['value'] == 'Linear' for option in options):
            return 'Linear'
        elif options and len(options) > 0:
            # Otherwise select the first sheet
            return options[0]['value']
        return current_value  # Keep current value if no options