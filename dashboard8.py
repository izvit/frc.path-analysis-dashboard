from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
from dash_bootstrap_templates import load_figure_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker, Query
import json

######################
## Setup Dash
######################
load_figure_template("darkly")
app = Dash(__name__,
            external_stylesheets=[dbc.themes.DARKLY],
            suppress_callback_exceptions=True,
            meta_tags=[{'name': 'viewport',
                        'content': 'width=device-width, initial-scale=1.0'}],
            )

######################
## Setup DB
######################
server = app.server
server.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{server.root_path}/../AdvantageScout/data_2024.db"
db = SQLAlchemy(server)
# reflect the tables
with app.server.app_context(): 
    db.Model.metadata.reflect(db.engine)

class Match(db.Model):
    __table__ = db.Model.metadata.tables['match']

######################
## Helper Objects
######################
event_colors = {
    "scoreSpeaker" : "#00FF00",
    "missSpeaker" : "red",
    "scoreAmp" : "blue",
    "missAmp" : "purple",
    "move" : "white",
    "pickup" : "orange",
    "drop" : "black",
    "init" : "cyan"
}

######################
## Helper Functions
######################
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
    red_wing_color = "#6E260E"
    blue_wing_color = "#000099"
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
                line=dict(color=red_wing_color, width=lwidth),
                layer=glayer
            ),
            #Blue wing line
            dict(
                type="line", x0=221, y0=0, x1=221, y1=300,
                line=dict(color=blue_wing_color, width=lwidth),
                layer=glayer
            ),
            #Blue Stage Triangle
            dict(
                type="path",
                path=" M 218 200 L 209 203 L 127 155 L 127 145 L 209 97 L 218 100 Z",
                line_color=blue_wing_color,
                layer=glayer
            ),
            #Red Stage Triangle
            dict(
                type="path",
                path=" M 390 200 L 397 203 L 480 155 L 480 145 L 397 97 L 390 100 Z",
                line_color=red_wing_color,
                layer=glayer
            ),
            #Blue speaker
            dict(
                type="path",
                path=" M 15 160 L 47 180 L 47 220 L 15 240 Z",
                fillcolor=blue_wing_color,
                line_color="#000000",
                layer=glayer
            ),
            #Red speaker
            dict(
                type="path",
                path=" M 590 160 L 558 180 L 558 220 L 590 240 Z",
                fillcolor=red_wing_color,
                line_color="#000000",
                layer=glayer
            ),
            #Blue source line
            dict(
                type="path",
                path=" M 590 60 L 525 20 L 525 0",
                line_color=blue_wing_color,
                layer=glayer
            ),
            #Red source line
            dict(
                type="path",
                path=" M 15 60 L 80 20 L 80 0",
                line_color=red_wing_color,
                layer=glayer
            ),
            #Blue amp line
            dict(
                type="path",
                path=" M 15 282 L 127 282 L 127 300",
                line_color=blue_wing_color,
                layer=glayer
            ),
            #Red amp line
            dict(
                type="path",
                path=" M 590 282 L 478 282 L 478 300",
                line_color=red_wing_color,
                layer=glayer
            ),
        ]
    )
    return True

def distance(pos0, pos1) -> np.double:
    return np.sqrt(np.power(pos0[0]-pos1[0],2) + np.power(pos0[1]-pos1[1],2))


@app.callback(
    Output(component_id='display-graph', component_property='figure'),
    Input(component_id='game-event-table', component_property='derived_virtual_data'),
    Input(component_id='game-event-table', component_property='derived_virtual_selected_rows'),
)
def update_field(all_rows_data, slcted_row_idx):
    def update_field_figure(display_fig, df):
            display_fig.data = [] 
            display_fig.layout.annotations=[]
            nrows=df.shape[0]
                       
            list_of_arrows = []
        
            print(df,flush=True)
            for i in range(nrows-1):
                pt0 = df.iloc[[i]].to_dict("records")[0]
                pt1 = df.iloc[[i+1]].to_dict("records")[0]
                arrow = go.layout.Annotation(dict(
                        x=pt1["x"],
                        y=pt1["y"],
                        xref="x", yref="y",
                        text="",
                        axref="x", ayref="y",
                        ax=pt0["x"],
                        ay=pt0["y"],
                        arrowhead=2,
                        arrowwidth=2,
                        arrowcolor='rgb(150,150,150)'
                        ))
                list_of_arrows.append(arrow)
              
            
            display_fig.update_layout(annotations=list_of_arrows)

            if nrows>0:
                event_types=df["name"].unique()
                for type in event_types:
                    if type=="move":
                        continue

                    display_fig.add_trace(go.Scatter(
                        x=df.loc[df['name'] == type]["x"].to_list(),
                        y=df.loc[df['name'] == type]["y"].to_list(),
                        xaxis='x',
                        yaxis='y',
                        mode='markers',
                        marker=dict(
                            symbol='0',
                            color=event_colors[type],
                            size=15
                        ),
                        name="Field events",
                        hoverinfo='none',
                    ))



            return display_fig
    
    print(f"all_rows_data: {all_rows_data}")
    if all_rows_data is not None and len(all_rows_data)>0:
        df = pd.DataFrame(all_rows_data)
        df["x"] = df["npos.x"]*600
        df["y"] = (1-df["npos.y"])*300
    else:
        df=pd.DataFrame()
        df["x"]=[]
        df["y"]=[]

    new_display_fig = update_field_figure(display_fig=display_fig, df = df)
    return new_display_fig


@app.callback(
    Output(component_id='game-event-table', component_property='data'),
    Input(component_id='team-select', component_property='value'),
    Input(component_id='match-select', component_property='value'),
    Input(component_id='game-stage', component_property='value'),
    Input(component_id='event-type-filter', component_property='value')
)
def get_match_data(team, match, stage, event_types):
    
    if match is not None:

        if stage=="Auto":
            table="AutoEventList"
        else:
            table="TeleEventList"

        df=pd.read_sql_query(f"SELECT {table} FROM match WHERE Team={team} and Match={match}", con=db.engine)
        df = df.reset_index(drop=True)
        
        result = [json.loads(x) for x in df[table] if x is not None]
        if len(result)>0:
            #Parse EventList json map into a list
            flat = pd.json_normalize(result[0]).to_dict(orient='records')
            flat = [{"id":i, **x} for i, x in enumerate(flat)]
            
            #Apply event list filter
            filtered =[i for i in flat if i["name"] in event_types]
            
            
            return  filtered
    
    return []


@app.callback(
    Output(component_id='match-select', component_property='options'),
    Output(component_id='match-select', component_property='value'),
    Input(component_id='team-select', component_property='value'),
)
def update_matches(team):
    df = pd.read_sql_query(f"SELECT DISTINCT Match FROM match WHERE Team={team}", con=db.engine)
    df = df.rename(columns={'Match': 'label'})
    df["value"] = df["label"]
    df = df[['label', 'value']].sort_values('label').reset_index(drop=True)
    options = df.to_dict('records')
    if df.shape[0]>0:
        value=df.iloc[0]["value"];
    else:
        value=None
    return options, value

@app.callback(
    Output(component_id='team-select', component_property='options'),
    Input(component_id='team-options', component_property='data'),
)
def update_teams(team_options):
     print(team_options)
     return team_options

@app.callback(
    Output(component_id='team-options', component_property='data'),
    Input(component_id='team-options', component_property='data'),
)
def get_teams(data):
    teams_df = pd.read_sql_query("SELECT DISTINCT Team FROM match", con=db.engine)
    teams_df = teams_df.rename(columns={'Team': 'label'})
    teams_df["value"] = teams_df["label"]
    teams_df = teams_df[['label', 'value']].sort_values('label').reset_index(drop=True)
    teams_options = teams_df.to_dict('records')

    return teams_options

######################
## Create Components
######################

# create plotly figure, draw court, and create container for the court figure
display_fig = go.Figure()

draw_plotly_field(display_fig, show_title=False, labelticks=False, show_axis=False,
                  glayer='below', bg_color='black', margins=0)



display_graph = dcc.Graph(
    id='display-graph',
    figure=display_fig,
    config={'staticPlot': False,
            'scrollZoom': False,
            },
)

heatmap_fig = go.Figure()
fig = px.density_heatmap([])

heatmap_graph = dcc.Graph(
    id='heatmap-figure', 
    figure=heatmap_fig,
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
    persistence=False,
    className='mb-3'
)

stage_dropdown = dcc.Dropdown(
    id='game-stage', multi=False, placeholder='Select Stage...',
    options=["Auto", "Teleop"],
    searchable=True,
    clearable=False,
    value="Auto",
    persistence=False,
    className='mb-3'
)

event_type_filter_dropdown = html.Div([
    dbc.DropdownMenu([
        dcc.Checklist(
            id='event-type-filter',
            options=[{"label":"move", "value":"move"},
                     {"label":"pickup", "value":"pickup"},
                     {"label":"drop", "value":"drop"},
                     {"label":"scoreSpeaker", "value":"scoreSpeaker"},
                     {"label":"missSpeaker", "value":"missSpeaker"},
                     {"label":"scoreAmp", "value":"scoreAmp"},
                     {"label":"missAmp", "value":"missAmp"},
                     {"label":"init", "value":"init"}],
            value=["move", "pickup", "drop", "scoreSpeaker", "missSpeaker", "scoreAmp", "missAmp", "init"],
            labelStyle={'display': 'block'},
            className='ml-1'
        ),
    ],
        id='event-type-filter-dropdown',
        direction="up",
        label="Event Filters",
        color="black",
        className='mb-1',
        toggle_style={'width': '100%'},
    )],
)

match_dropdown = dcc.Dropdown(
    id='match-select', multi=False, placeholder='Select Match...',
    options=[],
    searchable=True,
    clearable=False,
    value=1629636,
    persistence=False,
    className='mb-3'
)


######################
## Dashboard
######################

dashboard_page = dbc.Container([
    dcc.Store(id='team-options', storage_type='memory', data=[]),
    dcc.Store(id='event-filters', storage_type='memory', data=[]),
    dcc.Store(id="curr_match_df", storage_type='memory', data=[]),
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
            match_dropdown,
            stage_dropdown,
            event_type_filter_dropdown  
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
            className="justify-content-center"
        ),
        #########################################
        ]),
    dbc.Row([

        dbc.Col([
            html.H5("Match Events",
                    className='mt-4 mb-4 text-center'),
            dash_table.DataTable(
                id='game-event-table',
                columns=[
                    dict( id="id", name="Event ID"),
                    dict( id='name', name='Event' ),
                    dict( id='npos.x', name='Normalized X Position', type='numeric' ),
                    dict( id='npos.y', name='Normalize Y Position' , type='numeric' ),
                    dict( id='time', name='Time' , type='numeric' ),
                ],
                style_cell={
                    "fontFamily": "Ubuntu", 
                    "fontSize": "20px", 
                    "width": "75px",
                    "whiteSpace": "nowrap",
                    "textAlign": "center",
                    "border": 'none', 
                    "color" : 'black'
                },
                style_header={
                    "height": "50px",
                    "whiteSpace": "normal",
                    "backgroundColor": "rgb(100,100,100)",
                    "fontWeight": "bold",
                    "color":"yellow"
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(250,250,250)',
                    }
                ],
                style_table={'border': 'none'},
                cell_selectable=False,
                sort_action='native',
                filter_action='native'
            )
        ], 
        width=12,
        style={'paddingRight': '5rem'}
        )
    ])
])


######################
## NavBar
######################
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


######################
## Main Layout
######################

content = html.Div(id='page-content', children=[dashboard_page])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navigation_bar,
    content
])





if __name__ == '__main__':
    app.run(debug=True)
