from dash import html, dcc, dash_table
import plotly.graph_objects as go
import pandas as pd

def create_qa_checks(data_results=None):
    """
    Create quality assurance visualizations for the data.
    
    Args:
        data_results (dict): Dictionary containing the processed dataframes
        
    Returns:
        html.Div: The QA checks component
    """
    if data_results is None:
        return html.Div([
            html.H3("Quality Assurance Checks"),
            html.P("Load data to generate QA checks")
        ])
    
    # Extract data
    entities = data_results["vp_entities"]
    attributes = data_results["vp_attributes"]
    relationships = data_results["vp_relationships"]
    
    # Create a div for QA checks
    qa_div = html.Div([
        html.H3("Quality Assurance Checks"),
        
        # System mismatches
        html.Div([
            html.H4("System Mismatches"),
            html.Div(create_system_mismatch_tables(entities, attributes))
        ]),
        
        # Relationship checks
        html.Div([
            html.H4("Relationship Checks"),
            html.Div(create_relationship_checks(relationships, entities))
        ]),
        
        # Entity statistics
        html.Div([
            html.H4("Entity Statistics"),
            html.Div(create_entity_statistics(entities, attributes))
        ])
    ])
    
    return qa_div

def create_system_mismatch_tables(entities, attributes):
    """Create tables for system mismatches in entities and attributes."""
    # Entity mismatches
    entity_mismatches = entities[entities["Entity System"] == "entity missmatch"]
    
    if len(entity_mismatches) > 0:
        entity_table = dash_table.DataTable(
            id="entity-mismatch-table",
            columns=[{"name": c, "id": c} for c in ["Entity ID", "Entity Name"]],
            data=entity_mismatches[["Entity ID", "Entity Name"]].to_dict("records"),
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"},
            style_cell={"textAlign": "left"},
            page_size=10
        )
        entity_mismatch_div = html.Div([
            html.H5(f"Entity Mismatches ({len(entity_mismatches)}):"),
            entity_table
        ])
    else:
        entity_mismatch_div = html.Div([
            html.H5("Entity Mismatches (0):"),
            html.P("No entity mismatches found.")
        ])
    
    # Attribute mismatches
    attribute_mismatches = attributes[attributes["Attribute System"] == "attribute missmatch"]
    
    if len(attribute_mismatches) > 0:
        attribute_table = dash_table.DataTable(
            id="attribute-mismatch-table",
            columns=[{"name": c, "id": c} for c in ["Attribute ID", "Attribute Name", "Part Of Parent ID"]],
            data=attribute_mismatches[["Attribute ID", "Attribute Name", "Part Of Parent ID"]].to_dict("records"),
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "lightgrey", "fontWeight": "bold"},
            style_cell={"textAlign": "left"},
            page_size=10
        )
        attribute_mismatch_div = html.Div([
            html.H5(f"Attribute Mismatches ({len(attribute_mismatches)}):"),
            attribute_table
        ])
    else:
        attribute_mismatch_div = html.Div([
            html.H5("Attribute Mismatches (0):"),
            html.P("No attribute mismatches found.")
        ])
    
    return [entity_mismatch_div, attribute_mismatch_div]

def create_relationship_checks(relationships, entities):
    """Create visualizations for relationship checks."""
    # Check for missing entities in relationships
    entity_names = set(entities["Entity Name"])
    missing_parents = set()
    missing_children = set()
    
    for _, rel in relationships.iterrows():
        parent = rel["Entity Parent"]
        child = rel["Entity Child"]
        
        if parent not in entity_names:
            missing_parents.add(parent)
        
        if child not in entity_names:
            missing_children.add(child)
    
    # Create the missing entities div
    if missing_parents or missing_children:
        missing_div = html.Div([
            html.H5("Missing Entities in Relationships:"),
            html.Div([
                html.P(f"Missing Parent Entities ({len(missing_parents)}):"),
                html.Ul([html.Li(p) for p in sorted(missing_parents)]) if missing_parents else html.P("None")
            ]),
            html.Div([
                html.P(f"Missing Child Entities ({len(missing_children)}):"),
                html.Ul([html.Li(c) for c in sorted(missing_children)]) if missing_children else html.P("None")
            ])
        ])
    else:
        missing_div = html.Div([
            html.H5("Missing Entities in Relationships:"),
            html.P("No missing entities found in relationships.")
        ])
    
    # Create relationship type distribution
    rel_types = relationships["Entity Child Type"].value_counts().reset_index()
    rel_types.columns = ["Type", "Count"]
    
    fig = go.Figure(data=[
        go.Pie(
            labels=rel_types["Type"],
            values=rel_types["Count"],
            hole=.3,
            textinfo="label+percent"
        )
    ])
    
    fig.update_layout(
        title="Relationship Types Distribution",
        height=300
    )
    
    rel_type_div = html.Div([
        html.H5("Relationship Types:"),
        dcc.Graph(id="relationship-types-pie", figure=fig)
    ])
    
    return [missing_div, rel_type_div]

def create_entity_statistics(entities, attributes):
    """Create visualizations for entity statistics."""
    # Count attributes per entity
    entity_attribute_counts = attributes.groupby("Part Of Parent ID").size().reset_index(name="Attribute Count")
    
    # Merge with entity names
    entity_stats = pd.merge(
        entities[["Entity ID", "Entity Name"]],
        entity_attribute_counts,
        left_on="Entity ID",
        right_on="Part Of Parent ID",
        how="left"
    )
    
    entity_stats["Attribute Count"] = entity_stats["Attribute Count"].fillna(0).astype(int)
    entity_stats = entity_stats.sort_values("Attribute Count", ascending=False)
    
    # Create bar chart for top entities by attribute count
    top_n = 15
    top_entities = entity_stats.head(top_n)
    
    fig = go.Figure(data=[
        go.Bar(
            x=top_entities["Entity Name"],
            y=top_entities["Attribute Count"],
            marker_color="royalblue"
        )
    ])
    
    fig.update_layout(
        title=f"Top {top_n} Entities by Attribute Count",
        xaxis_title="Entity",
        yaxis_title="Number of Attributes",
        xaxis_tickangle=-45,
        height=400
    )
    
    attribute_count_div = html.Div([
        html.H5("Attribute Count by Entity:"),
        dcc.Graph(id="entity-attribute-count", figure=fig)
    ])
    
    # Create system distribution
    system_counts = entities["Entity System"].value_counts().reset_index()
    system_counts.columns = ["System", "Count"]
    
    fig2 = go.Figure(data=[
        go.Pie(
            labels=system_counts["System"],
            values=system_counts["Count"],
            hole=.3,
            textinfo="label+percent"
        )
    ])
    
    fig2.update_layout(
        title="Entity System Distribution",
        height=300
    )
    
    system_div = html.Div([
        html.H5("Entity System Distribution:"),
        dcc.Graph(id="entity-system-pie", figure=fig2)
    ])
    
    return [attribute_count_div, system_div]