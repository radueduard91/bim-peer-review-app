import os
import pandas as pd

def get_data_folders():
    """Get the project root folder and data folder paths."""
    project_root = r"C:\Users\R40008\Asset Model Server\python\bim-testing-app"
    data_folder = os.path.join(r"C:\Users\R40008\Asset Model Server\python\data", "bim-visualisation-app")
    
    return {
        "project_root": project_root,
        "data_folder": data_folder
    }

def load_vp_files(vp_file_path):
    """
    Load VP Excel file and extract the Entity, Column, and Foreign Key sheets.
    
    Args:
        vp_file_path (str): Path to the VP Excel file
        
    Returns:
        tuple: (vp_entities, vp_attributes, vp_relationships) as DataFrames
    """
    # Load Entity sheet
    entity_sheet = pd.read_excel(vp_file_path, sheet_name="Entity")
    
    # Apply initial transformations to match Power Query steps
    vp_entities = entity_sheet.copy()
    vp_entities.columns = vp_entities.iloc[0]  # Promote headers
    vp_entities = vp_entities.iloc[1:].reset_index(drop=True)  # Remove header row
    
    # Change column types (simplified for brevity)
    vp_entities["ID"] = pd.to_numeric(vp_entities["ID"], errors="coerce")
    vp_entities["Model ID"] = pd.to_numeric(vp_entities["Model ID"], errors="coerce")
    vp_entities["Diagram ID"] = pd.to_numeric(vp_entities["Diagram ID"], errors="coerce")
    vp_entities["Parent ID"] = pd.to_numeric(vp_entities["Parent ID"], errors="coerce")
    
    # Remove unnecessary columns
    vp_entities = vp_entities[["ID", "Name", "Description"]]
    
    # Load Column sheet (attributes)
    column_sheet = pd.read_excel(vp_file_path, sheet_name="Column")
    
    # Apply initial transformations to match Power Query steps
    vp_attributes = column_sheet.copy()
    vp_attributes.columns = vp_attributes.iloc[0]  # Promote headers
    vp_attributes = vp_attributes.iloc[1:].reset_index(drop=True)  # Remove header row
    
    # Change column types (simplified for brevity)
    vp_attributes["ID"] = pd.to_numeric(vp_attributes["ID"], errors="coerce")
    vp_attributes["Model ID"] = pd.to_numeric(vp_attributes["Model ID"], errors="coerce")
    vp_attributes["Parent ID"] = pd.to_numeric(vp_attributes["Parent ID"], errors="coerce")
    
    # Keep only needed columns
    vp_attributes = vp_attributes[["ID", "Name", "Description", "PrimaryKey", "Parent Name"]]
    
    # Load Foreign Key sheet (relationships)
    fk_sheet = pd.read_excel(vp_file_path, sheet_name="Foreign Key")
    
    # Apply initial transformations to match Power Query steps
    vp_relationships = fk_sheet.copy()
    vp_relationships.columns = vp_relationships.iloc[0]  # Promote headers
    vp_relationships = vp_relationships.iloc[1:].reset_index(drop=True)  # Remove header row
    
    # Change column types (simplified for brevity)
    vp_relationships["ID"] = pd.to_numeric(vp_relationships["ID"], errors="coerce")
    vp_relationships["Table"] = pd.to_numeric(vp_relationships["Table"], errors="coerce")
    vp_relationships["Reference"] = pd.to_numeric(vp_relationships["Reference"], errors="coerce")
    
    # Keep only needed columns
    vp_relationships = vp_relationships[["Table", "Reference", "Identifying"]]
    
    return vp_entities, vp_attributes, vp_relationships

def load_central_doc(central_doc_path, sheet_name="Linear"):
    """
    Load the Central Document Excel file and extract object and attribute system labels.
    
    Args:
        central_doc_path (str): Path to the Central Document Excel file
        sheet_name (str): Name of the sheet to load (default is "Linear")
        
    Returns:
        tuple: (central_doc_object_labels, central_doc_attribute_labels) as DataFrames
    """
    # Load specified sheet
    try:
        central_doc = pd.read_excel(central_doc_path, sheet_name=sheet_name)
    except Exception as e:
        raise ValueError(f"Error loading sheet '{sheet_name}': {str(e)}")
    
    # Promote headers if needed (assuming they're already proper headers)
    
    # Object labels processing
    object_labels = central_doc.copy()
    
    # Rename columns to match the expected structure
    if "BIM Object" not in object_labels.columns or "Source System" not in object_labels.columns:
        raise ValueError("Required columns 'BIM Object' and 'Source System' not found in the sheet")
    
    # Filter and process according to Power Query steps
    object_labels = object_labels[["BIM Object", "Source System"]]
    object_labels = object_labels[~object_labels["BIM Object"].astype(str).str.startswith("skip")]
    object_labels = object_labels.drop_duplicates()
    
    # Group by BIM Object and combine systems with comma
    grouped_systems = object_labels.groupby("BIM Object")["Source System"].apply(
        lambda x: ", ".join(x.unique())
    ).reset_index()
    grouped_systems.rename(columns={"Source System": "System"}, inplace=True)
    
    # Merge with original and keep unique rows
    central_doc_object_labels = grouped_systems.drop_duplicates()
    
    # Attribute labels processing
    attribute_labels = central_doc.copy()
    
    # Filter and process according to Power Query steps
    if "BIM Attribute" not in attribute_labels.columns:
        raise ValueError("Required column 'BIM Attribute' not found in the sheet")
    
    attribute_labels = attribute_labels[["BIM Attribute", "Source System"]]
    attribute_labels = attribute_labels[~attribute_labels["BIM Attribute"].astype(str).str.startswith("skip")]
    attribute_labels = attribute_labels.drop_duplicates()
    
    # Group by BIM Attribute and combine systems with comma
    grouped_attr_systems = attribute_labels.groupby("BIM Attribute")["Source System"].apply(
        lambda x: ", ".join(x.unique())
    ).reset_index()
    grouped_attr_systems.rename(columns={"Source System": "System"}, inplace=True)
    
    # Merge with original and keep unique rows
    central_doc_attribute_labels = grouped_attr_systems.drop_duplicates()
    
    return central_doc_object_labels, central_doc_attribute_labels