from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
import networkx as nx
import random

def create_data_diagram(data_results=None):
    """
    Create a network diagram visualization of the data model.
    
    Args:
        data_results (dict): Dictionary containing the processed dataframes
        
    Returns:
        html.Div: The data diagram component
    """
    if data_results is None:
        return html.Div([
            html.H3("Data Model Diagram"),
            html.P("Load data to generate diagram")
        ])
    
    # Extract data
    entities = data_results["vp_entities"]
    relationships = data_results["vp_relationships"]
    
    # Create network graph
    G = nx.DiGraph()
    
    # Add nodes (entities)
    for _, entity in entities.iterrows():
        system = entity["Entity System"]
        if pd.isna(system):
            system = "Unknown"
        
        G.add_node(
            entity["Entity Name"],
            id=entity["Entity ID"],
            description=entity["Entity Description"] if not pd.isna(entity["Entity Description"]) else "",
            system=system
        )
    
    # Add edges (relationships)
    for _, rel in relationships.iterrows():
        parent = rel["Entity Parent"]
        child = rel["Entity Child"]
        rel_type = rel["Entity Child Type"]
        
        # Only add edge if both nodes exist
        if parent in G.nodes and child in G.nodes:
            G.add_edge(parent, child, type=rel_type)
    
    # Create Plotly network graph
    pos = nx.spring_layout(G, seed=42)  # Position nodes using a force-directed layout
    
    # Prepare node traces
    node_traces = {}
    systems = set()
    
    # Collect all systems
    for node, attrs in G.nodes(data=True):
        system = attrs.get("system", "Unknown")
        systems.add(system)
    
    # Create a color map for systems
    color_map = {}
    colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
    ]
    
    for i, system in enumerate(systems):
        color_map[system] = colors[i % len(colors)]
    
    # Create node traces for each system
    for system in systems:
        node_traces[system] = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            name=system,
            marker=dict(
                color=color_map[system],
                size=15,
                line=dict(width=2, color='white')
            )
        )
    
    # Fill node traces
    for node, attrs in G.nodes(data=True):
        x, y = pos[node]
        system = attrs.get("system", "Unknown")
        node_id = attrs.get("id", "")
        desc = attrs.get("description", "")
        
        hover_text = f"Entity: {node}<br>ID: {node_id}<br>System: {system}"
        if desc:
            hover_text += f"<br>Description: {desc}"
            
        node_traces[system]['x'] = node_traces[system]['x'] + (x,)
        node_traces[system]['y'] = node_traces[system]['y'] + (y,)
        node_traces[system]['text'] = node_traces[system]['text'] + (hover_text,)
    
    # Create edge trace
    edge_x = []
    edge_y = []
    edge_text = []
    
    for edge in G.edges(data=True):
        source, target, attrs = edge
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
        rel_type = attrs.get("type", "")
        edge_text.append(f"{source} → {target}<br>Type: {rel_type}")
    
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='text',
        text=edge_text,
        mode='lines'
    )
    
    # Create the figure
    fig = go.Figure(
        layout=go.Layout(
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            title="Data Model Relationships"
        )
    )
    
    # Add all traces to the figure
    fig.add_trace(edge_trace)
    for system in systems:
        fig.add_trace(node_traces[system])
    
    # Create the diagram component
    return html.Div([
        html.H3("Data Model Diagram"),
        dcc.Graph(
            id='data-model-graph',
            figure=fig,
            style={'height': '800px'}
        ),
        html.Div([
            html.H4("Legend"),
            html.Ul([
                html.Li([
                    html.Span(style={'background-color': color_map[system], 'width': '20px', 'height': '20px', 'display': 'inline-block', 'margin-right': '5px'}),
                    f"{system} System"
                ]) for system in systems
            ])
        ])
    ])