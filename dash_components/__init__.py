# This file is intentionally left empty to make the directory a Python package

# Register all component callbacks
def register_callbacks(app):
    """Register all component callbacks with the Dash app."""
    from dash_components.file_selector import register_file_selector_callbacks
    from dash_components.sheet_selector import register_sheet_selector_callbacks
    
    register_file_selector_callbacks(app)
    register_sheet_selector_callbacks(app)