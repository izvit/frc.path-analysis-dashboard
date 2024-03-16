from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from dash_bootstrap_templates import load_figure_template

load_figure_template("darkly")

app = Dash(__name__,
           external_stylesheets=[dbc.themes.DARKLY],
            suppress_callback_exceptions=True,
            meta_tags=[{'name': 'viewport',
                        'content': 'width=device-width, initial-scale=1.0'}],
            )


def draw_plotly_field(fig, fig_width=600, fig_height=300, margins=30, lwidth=3,
                      show_title=True, labelticks=True, show_axis=True,
                      glayer='below', bg_color='white'):


    fig.update_xaxes(showgrid=False, 
                     zeroline=False, 
                     range=[0,600], 
                     fixedrange=True,
                     visible=show_title)
    fig.update_yaxes(showgrid=False, 
                     zeroline=False, 
                     range=[0,300], 
                     fixedrange=True,
                     visible=show_title)
    fig.update_layout(
                showlegend=False,
                autosize=False,
                width=fig_width,
                height=fig_height,
                margin=dict(l=margins, r=margins, t=margins, b=margins),
            )

    main_line_col = "#000000"
    fig.update_layout(
        # Line Horizontal
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        yaxis=dict(
            scaleanchor="x",
            scaleratio=1,
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            fixedrange=True,
            visible=show_axis,
            showticklabels=labelticks,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            fixedrange=True,
            visible=show_axis,
            showticklabels=labelticks,
        ),
        yaxis2=dict(
            scaleanchor="x2",
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            fixedrange=True,
            visible=show_axis,
            showticklabels=labelticks,
        ),
        xaxis2=dict(
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            fixedrange=True,
            visible=show_axis,
            showticklabels=labelticks,
        ),
        shapes=[
            # Field border
            dict(
                type="rect", x0=15, y0=300, x1=590, y1=0,
                line=dict(color=main_line_col, width=lwidth),
                # fillcolor='#333333',
                layer=glayer
            ), 
            # Center line
            dict(
                type="line", x0=305, y0=0, x1=305, y1=300,
                line=dict(color="#666666", width=lwidth),
                layer=glayer
            ),

            # Red wing line
            dict(
                type="line", x0=387, y0=0, x1=387, y1=300,
                line=dict(color="#FF0000", width=lwidth),
                layer=glayer
            ),
            #Blue wing line
            dict(
                type="line", x0=221, y0=0, x1=221, y1=300,
                line=dict(color="#0000FF", width=lwidth),
                layer=glayer
            ),
            #Blue Stage Triangle
            dict(
                type="path",
                path=" M 218 200 L 209 203 L 127 155 L 127 145 L 209 97 L 218 100 Z",
                line_color="#0000FF",
                layer=glayer
            ),
            #Red Stage Triangle
            dict(
                type="path",
                path=" M 390 200 L 397 203 L 480 155 L 480 145 L 397 97 L 390 100 Z",
                line_color="#FF0000",
                layer=glayer
            ),
            #Blue speaker
            dict(
                type="path",
                path=" M 15 160 L 47 180 L 47 220 L 15 240 Z",
                fillcolor="#0000ff",
                line_color="#000000",
                layer=glayer
            ),
            #Red speaker
            dict(
                type="path",
                path=" M 590 160 L 558 180 L 558 220 L 590 240 Z",
                fillcolor="#ff0000",
                line_color="#000000",
                layer=glayer
            ),
            #Blue source line
            dict(
                type="path",
                path=" M 590 60 L 525 20 L 525 0",
                line_color="#0000ff",
                layer=glayer
            ),
            #Red source line
            dict(
                type="path",
                path=" M 15 60 L 80 20 L 80 0",
                line_color="#ff0000",
                layer=glayer
            ),
            #Blue amp line
            dict(
                type="path",
                path=" M 15 282 L 127 282 L 127 300",
                line_color="#0000ff",
                layer=glayer
            ),
            #Red amp line
            dict(
                type="path",
                path=" M 590 282 L 478 282 L 478 300",
                line_color="#ff0000",
                layer=glayer
            ),
        ]
    )
    return True

@app.callback(
    Output(component_id='display-graph', component_property='figure'),
    Input(component_id="team-select", component_property="value"),
    Input(component_id="match-select", component_property="value")
)
def update_data(team_select, match_select):
    def update_court_figure(display_fig, df):
            display_fig.data = [] 
            display_fig.add_trace(go.Histogram2dContour( 
                x=df['x'].to_list(),
                y=df['y'].to_list(),
                colorscale=['rgb(255, 255, 255)'] + px.colors.sequential.Magma[1:][::-1],
                xaxis='x',
                yaxis='y',
                showscale=False,
                line=dict(width=0),
                hoverinfo='none',
            ))
            display_fig.add_trace(go.Scatter(
                x=df['x'].to_list(),
                y=df['y'].to_list(),
                xaxis='x',
                yaxis='y',
                mode='markers',
                marker=dict(
                    symbol='x',
                    color='black',
                    size=4
                ),
                name="Field Heatmap",
                hoverinfo='none',
            ))

            # ##########################################################################################
            # ######################### HOW TO ADD ANNOTATIONS TO SCATTER PLOT #########################
            # # https://chart-studio.plotly.com/~empet/15366/customdata-for-a-few-plotly-chart-types/#/#
            # ##########################################################################################
            # display_fig.update_traces(
            #     customdata=[],
            #     selector=dict(type='scatter'),
            #     hovertemplate=None)
            
            # ##Field background
            # display_fig.add_layout_image(
            #     dict(
            #         source=app.get_asset_url('frc_field_full.jpg'),
            #         xref="x",
            #         yref="y",
            #         x=0,
            #         y=300,
            #         sizex=600,
            #         sizey=300,
            #         xanchor="left",
            #         sizing="stretch",
            #         layer="below"))
            


            return display_fig
    
    df = pd.DataFrame()
    if team_select=="6328":
        df['x']=[10,20,30,40]
        df['y']=[30,40,50,60]
    else:
        df['x']=[61,72,93,94]
        df['y']=[73,64,55,46]

    new_display_fig = update_court_figure(display_fig=display_fig, df = df)
    return new_display_fig
 



# create plotly figure, draw court, and create container for the court figure
display_fig = go.Figure()

draw_plotly_field(display_fig, show_title=False, labelticks=False, show_axis=False,
                  glayer='above', bg_color='white', margins=0)



display_graph = dcc.Graph(
    id='display-graph',
    figure=display_fig,
    config={'staticPlot': False,
            'scrollZoom': False,
            },
)

team_dropdown = dcc.Dropdown(
    id='team-select', multi=False, placeholder='Select Team...',
    options=[],
    searchable=True,
    clearable=False,
    value=1629636,
    persistence=True,
    className='mb-3'
)

match_dropdown = dcc.Dropdown(
    id='match-select', multi=False, placeholder='Select Match...',
    options=[],
    searchable=True,
    clearable=False,
    value=1629636,
    persistence=True,
    className='mb-3'
)

dashboard_page = dbc.Container([
      dbc.Row([
        #########################################
        #### FIRST COLUMN OF DASHBOARD PAGE ####
        dbc.Col([
            html.H4("Team",
                    className='mt-2 text-center',
                    style={'font=size': '14px'}),
            html.Hr(className="my-2"),
            team_dropdown,
            html.H4("Match",
                    className='mt-2 text-center',
                    style={'font=size': '14px'}),
            html.Hr(className="my-2"),
            match_dropdown
        ],
            width=2,
            className='ml-0 mr-0',
        ),
        #########################################

        #########################################
        #### SECOND COLUMN OF DASHBOARD PAGE ####
        dbc.Col([
             html.H4("Field",
                    className='mt-2 text-center',
                    style={'font=size': '14px'}),
            html.Hr(className="my-2"),
            display_graph,
        ],
            width=7,
            style={'margin-right': '0px',
                   'margin-left': '0px'
                   },
            className="justify-content-center"
        ),
        #########################################
        ])
        ])



navigation_bar = html.Div(
    dbc.NavbarSimple([
        dbc.NavLink("Interactive Dashboard", href="/dashboard", active='exact', id='dashboard-'),
    ],
        dark=True,
        color='#0047AB',
        brand='Robot Path Analyzer',
        brand_href='#',
        className='py-lg-0',
    )
)


content = html.Div(id='page-content', children=[dashboard_page])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navigation_bar,
    content
])


if __name__ == '__main__':
    app.run(debug=True)
