import os
from dash import html, dcc
from dash.dependencies import Input, Output, State

def create_file_selector(id_prefix, label, default_path=""):
    """
    Create a file selector component for the dashboard.
    
    Args:
        id_prefix (str): Prefix for the component IDs
        label (str): Label text for the file selector
        default_path (str): Default file path to display
        
    Returns:
        html.Div: The file selector component
    """
    return html.Div([
        html.Label(label),
        html.Div([
            dcc.Input(
                id=f"{id_prefix}-path",
                type="text",
                value=default_path,
                placeholder="File path...",
                style={"width": "70%", "marginRight": "10px"}
            ),
            html.Button(
                "Browse", 
                id=f"{id_prefix}-browse",
                style={"width": "20%"}
            ),
            dcc.Upload(
                id=f"{id_prefix}-upload",
                children=html.Div(['Drag and Drop or ']),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px 0'
                },
                multiple=False
            ),
        ]),
        html.Div(id=f"{id_prefix}-output")
    ], className="file-selector")

def register_file_selector_callbacks(app):
    """
    Register callbacks for the file selector component.
    
    Args:
        app: The Dash app
    """
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
    
    # In a real application, you would add more callbacks for the browse buttons
    # to actually browse the file system. Since this requires additional libraries
    # and OS-specific handling, I'm simplifying for this example.
    # For a complete implementation, consider using:
    # - tkinter.filedialog
    # - PyQt file dialog
    # - A custom solution involving the file system and browser uploads

    # Example for handling browse button clicks (placeholder)
    @app.callback(
        Output("vp-file-path", "value"),
        [Input("vp-file-browse", "n_clicks")],
        [State("vp-file-path", "value")]
    )
    def browse_vp_file(n_clicks, current_path):
        if n_clicks is None or n_clicks == 0:
            return current_path
        
        # This would be where you'd implement file browsing
        # For example:
        # from tkinter import Tk, filedialog
        # root = Tk()
        # root.withdraw()
        # file_path = filedialog.askopenfilename(
        #     title="Select VP Excel File",
        #     filetypes=[("Excel files", "*.xlsx;*.xls")]
        # )
        # return file_path if file_path else current_path
        
        return current_path  # Placeholder
    
    @app.callback(
        Output("central-doc-path", "value"),
        [Input("central-doc-browse", "n_clicks")],
        [State("central-doc-path", "value")]
    )
    def browse_central_doc_file(n_clicks, current_path):
        if n_clicks is None or n_clicks == 0:
            return current_path
            
        # Same implementation as above
        return current_path  # Placeholder