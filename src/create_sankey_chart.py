import pandas as pd
import plotly.graph_objects as go
from plotly.io import write_image

# Read the CSV file
df = pd.read_csv('/Users/max/Desktop/top_10_fields.csv')

# Ensure the required columns are present
required_columns = ['funding_type', 'class_name', 'occurence', 'occurence_per']
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"CSV file must contain the following columns: {', '.join(required_columns)}")

# Rename funding types
funding_type_mapping = {
    'industry': 'Industry Funded AI Paper',
    'non-industry': 'Non-Industry Funded AI Paper',
    'non-funded': 'Non-Funded AI Paper'
}

# Color scales for nodes
funding_type_colors = {"Industry Funded AI Paper": "#440154", "Non-Industry Funded AI Paper": "#3E4A89", "Non-Funded AI Paper": "#1F9E89"}
class_name_colors = ["#0D0887", "#44039E", "#6F00A8", "#9512A1", "#B6308B", 
                     "#D14E72", "#E76E5B", "#F79044", "#FEB72D", "#F0F921"]

def create_sankey_diagram(funding_type_data, funding_type):
    source = []
    target = []
    value = []
    link_labels = []

    # Create node labels
    node_labels = [funding_type]
    class_names = list(funding_type_data['class_name'])
    i = 1
    # Create edges and prepare link labels
    for _, row in funding_type_data.iterrows():
        source.append(0)  # Always 0 as we have only one source node
        target.append(i)  # +1 because the first node is the funding type
        value.append(row['occurence_per'])
        link_label = f"{row['class_name']} ({row['occurence']:,.1f}k, {row['occurence_per']:.1f}%)"
        link_labels.append(link_label)
        node_labels.append(link_label)
        i += 1

    # Create color list
    node_colors = [funding_type_colors[funding_type]] + class_name_colors[:len(funding_type_data)]

    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = node_labels,
          color = node_colors
        ),
        link = dict(
          arrowlen=8,
          source = source,
          target = target,
          value = value,
          label = link_labels,
          color = 'rgba(200, 200, 200, 0.5)'  # Semi-transparent gray
      ))])

    # Update the layout
    fig.update_layout(
        font_size=15,
        paper_bgcolor='white',  # Transparent background
        plot_bgcolor='white',   # Transparent plot area
        annotations=[
                      dict(
                x=0.5,  # Centered horizontally
                y=-0.082,  # Position it below the chart
                showarrow=False,
                text="Outgoing Citation Fields",
                xref="paper",
                yref="paper",
                font=dict(size=16),
                xanchor='center',
                yanchor='top'
            ),
            dict(
                x=0.628,  # Centered horizontally
                y=-0.15,  # Position it below the text
                showarrow=True,
                text="",
                xref="paper",
                yref="paper",
                arrowcolor="lightgrey",  # Black arrow color
                ax=-189,  # Positive ax to point the arrow to the right
                ay=0,  # No vertical offset
                arrowwidth=3,  # Thickness of the arrow
                arrowhead=2,  # Arrowhead size
                arrowsize=1,  # Size of the arrowhead
                xanchor='center',
                yanchor='top'
            )
        ],
        width=900,   # Assuming a 3:2 aspect ratio, 900 x 600
        height=600   # This is equivalent to height=5 in R's ggsave()
    )

    # Update the figure to ensure transparency
    fig.update_traces(node = dict(
        pad = 15,
        thickness = 20,
        label = node_labels,
        color = node_colors
    ),
    link = dict(
        color = 'rgba(200, 200, 200, 0.5)'
    ))

    return fig

# Function to create and display diagram for a specific funding type
def create_and_display_diagram(funding_type):
    renamed_funding_type = funding_type_mapping[funding_type]
    funding_type_data = df[df['funding_type'] == funding_type].sort_values('occurence_per', ascending=False)
    fig = create_sankey_diagram(funding_type_data, renamed_funding_type)
    # fig.show()
    output_path = "/Users/max/Desktop/non_funded_cit_fields.png"
    write_image(fig, output_path, scale=2.5)  # scale=2.5 for 300 DPI (120 * 2.5 = 300)

# industry': 'Industry Funded AI Paper',
#     'non-industry': 'Non-Industry Funded AI Paper',
#     'non-funded': 'Non-Funded AI Paper'
create_and_display_diagram('non-funded')