import pandas as pd

def process_data(vp_entities, vp_attributes, vp_relationships, central_doc_object_labels, central_doc_attribute_labels):
    """
    Apply transformations to the loaded dataframes based on Power Query logic.
    
    Args:
        vp_entities (DataFrame): Entity data from VP
        vp_attributes (DataFrame): Attribute data from VP
        vp_relationships (DataFrame): Relationship data from VP
        central_doc_object_labels (DataFrame): Object system labels from Central Doc
        central_doc_attribute_labels (DataFrame): Attribute system labels from Central Doc
        
    Returns:
        dict: Dictionary containing all processed dataframes
    """
    # Process VP Entities
    processed_entities = process_vp_entities(vp_entities, central_doc_object_labels)
    
    # Process VP Attributes
    processed_attributes = process_vp_attributes(vp_attributes, central_doc_attribute_labels, processed_entities)
    
    # Process VP Relationships
    processed_relationships = process_vp_relationships(vp_relationships, vp_entities)
    
    return {
        "vp_entities": processed_entities,
        "vp_attributes": processed_attributes,
        "vp_relationships": processed_relationships,
        "central_doc_object_labels": central_doc_object_labels,
        "central_doc_attribute_labels": central_doc_attribute_labels
    }

def process_vp_entities(vp_entities, central_doc_object_labels):
    """Process VP Entities according to Power Query transformations."""
    # Merge with Object System Labels
    merged_entities = pd.merge(
        vp_entities,
        central_doc_object_labels,
        left_on="Name",
        right_on="BIM Object",
        how="left"
    )
    
    # Replace null values with "entity missmatch"
    merged_entities["System"] = merged_entities["System"].fillna("entity missmatch")
    
    # Remove unnecessary columns
    if "Model ID" in merged_entities.columns:
        merged_entities = merged_entities.drop(columns=["Model ID"])
    
    # Add Entity ID column
    merged_entities["Entity ID"] = range(1, len(merged_entities) + 1)
    
    # Reorder and rename columns
    result = merged_entities[["Entity ID", "Name", "Description", "System"]]
    result = result.rename(columns={
        "Name": "Entity Name",
        "Description": "Entity Description",
        "System": "Entity System"
    })
    
    return result

def process_vp_attributes(vp_attributes, central_doc_attribute_labels, processed_entities):
    """Process VP Attributes according to Power Query transformations."""
    # Merge with Attribute System Labels
    merged_attributes = pd.merge(
        vp_attributes,
        central_doc_attribute_labels,
        left_on="Name",
        right_on="BIM Attribute",
        how="left"
    )
    
    # Replace null values with "attribute missmatch"
    merged_attributes["System"] = merged_attributes["System"].fillna("attribute missmatch")
    
    # Remove unnecessary columns
    if "ID" in merged_attributes.columns:
        merged_attributes = merged_attributes.drop(columns=["ID"])
    if "Model ID" in merged_attributes.columns:
        merged_attributes = merged_attributes.drop(columns=["Model ID"])
    
    # Add Attribute ID column, starting from 10000
    merged_attributes["Attribute ID"] = range(10000, 10000 + len(merged_attributes))
    
    # Rename columns
    result = merged_attributes.rename(columns={
        "Name": "Attribute Name",
        "Description": "Attribute Description",
        "Parent Name": "Part Of Parent Name",
        "System": "Attribute System"
    })
    
    # Merge with processed entities to get Entity ID
    result = pd.merge(
        result,
        processed_entities[["Entity ID", "Entity Name"]],
        left_on="Part Of Parent Name",
        right_on="Entity Name",
        how="left"
    )
    
    # Reorder columns
    result = result.rename(columns={"Entity ID": "Part Of Parent ID"})
    result = result[["Attribute ID", "Attribute Name", "Part Of Parent ID", 
                    "Attribute Description", "PrimaryKey", "Attribute System"]]
    
    return result

def process_vp_relationships(vp_relationships, vp_entities):
    """Process VP Relationships according to Power Query transformations."""
    # Add Entity Names by joining with entities
    table_join = pd.merge(
        vp_relationships,
        vp_entities,
        left_on="Table",
        right_on="ID",
        how="left"
    )
    table_join = table_join.rename(columns={"Name": "Entity Child"})
    
    reference_join = pd.merge(
        table_join,
        vp_entities,
        left_on="Reference",
        right_on="ID",
        how="left"
    )
    reference_join = reference_join.rename(columns={"Name": "Entity Parent"})
    
    # Remove unnecessary columns
    result = reference_join[["Entity Parent", "Entity Child", "Identifying"]]
    
    # Sort by Entity Parent
    result = result.sort_values("Entity Parent")
    
    # Apply transformations to swap parent/child based on "Identifying" flag
    result = result.rename(columns={
        "Entity Parent": "Entity Parent-pre",
        "Entity Child": "Entity Child-pre"
    })
    
    # Apply the conditional logic for parent/child relationship based on Identifying flag
    result["Entity Parent"] = result.apply(
        lambda row: row["Entity Parent-pre"] if row["Identifying"] == "Yes" else row["Entity Child-pre"],
        axis=1
    )
    
    result["Entity Child"] = result.apply(
        lambda row: row["Entity Child-pre"] if row["Identifying"] == "Yes" else row["Entity Parent-pre"],
        axis=1
    )
    
    # Remove temporary columns and reorder
    result = result[["Entity Parent", "Entity Child", "Identifying"]]
    
    # Rename "Identifying" column to "Entity Child Type"
    result = result.rename(columns={"Identifying": "Entity Child Type"})
    
    # Replace values
    result["Entity Child Type"] = result["Entity Child Type"].replace("Yes", "Standard Entity")
    result["Entity Child Type"] = result["Entity Child Type"].replace("No", "Reference Data Table")
    
    return result