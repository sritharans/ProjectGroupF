import pathlib
import os

import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

colors = {
    'background': '#CD5C5C',
    'text': '#FDFEFE'
}


# app initialize
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)


server = app.server
app.config["suppress_callback_exceptions"] = True


# load data
# from pyhive import hive
# conn = hive.connect(host='10.242.134.39', port=10000, username='root', auth='NONE')
# cursor = conn.cursor()
# cursor.execute("select * from shopedata limit 1000")
# Shopedata = []
# for result in cursor.fetchall():
#     data = []
#     for i in result:
#         data.append(i)
#     Shopedata.append(data)
# cursor.close()
#
# df=pd.DataFrame(data=Shopedata,columns=['Label', 'Stars', 'Ratings', 'Sold', 'PriceMin', 'PriceMax', 'Stock',
#        'Seller', 'SellerRatings', 'Products', 'ResponseRate', 'ResponseTime',
#        'Joined', 'Followers', 'URL'])

df=pd.read_csv("/Users/liuhongyang/Desktop/ShData-master/dash-shope/data/Automotive.csv")

df.head()

df=df.dropna()
df=df.drop_duplicates(keep='first')
df1=df
# APP_PATH = str(pathlib.Path(__file__).parent.resolve())
AttributeName=["SellerRatings","Products","Followers","ResponseRate"]



# APP_PATH = str(pathlib.Path(__file__).parent.resolve())
# AttributeName=["SellerRatings","Products","Followers","ResponseRate"]
# df = pd.read_csv(os.path.join(APP_PATH, os.path.join("data", "Automotive.csv")))

def transform_time(response_rate, response_time):
    if response_time == 'hours':
        return response_rate
    elif response_time == 'days':
        a = response_rate * 24
        return a
    elif response_time == 'minutes':
        a= response_rate/60
        return a

df1['ResponseHour'] = df1.apply(lambda x: transform_time(x['ResponseRate'], x['ResponseTime']), axis=1)
Average_Res_Hour = df1.groupby('Seller')['ResponseHour'].mean().mean()



def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.H6("Shopee Seller Exploration Web App"),
        ],
    )


## graph title
def build_graph_title(title):
    return html.P(className="graph-title", children=title)




app.layout = html.Div(
    children=[
        html.Div(
            id="top-row",
            children=[

                html.Div(
                    className="row",
                    id="top-row-header",

                    children=[

                        html.Div(
                            id="header-container",
                            children=[
                                build_banner(),
                                html.P(
                                    id="instructions",
                                    children=[
                                        html.H5("Montoring the best seller/shop in different dimensions "),
                                        html.H6("SellerRatings - Number of ratings this seller has received"),
                                        html.H6("Products - Number of products this seller has in his/her shop"),
                                        html.H6("Followers - The number of customers following this seller's store"),
                                        html.H6("ResponseRate - Percentage of messages from customers this seller has responded to")
                                    ]
                                ),

                                build_graph_title("Select Your Preference "),

                                dcc.Dropdown(
                                    id="operator-select",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in AttributeName
                                    ],

                                    style={
                                                'textAlign': 'left',
                                                'color': colors['text']
                                            },
                                    multi=False,

                                    value=[
                                        ""
                                    ],
                                ),
                            ],
                        )

                    ],
                ),

            #---
                html.Div(
                    className="row",
                    id="top-row-graphs",
                    children=[

                        # Ternary map
                        html.Div(
                            id="ternary-map-container",
                            children=[


                                html.Div(
                                    id="ternary-header",
                                    children=[
                                        build_graph_title(
                                            "Seller/Shop Comparison"
                                        )

                                    ],
                                ),


                                dcc.Graph(
                                    id="ternary-map",
                                    figure={
                                        "layout": {
                                            "paper_bgcolor": "#192444",
                                            "plot_bgcolor": "#192444",
                                        }
                                    },
                                    config={
                                        "scrollZoom": True,
                                        "displayModeBar": False,
                                    },
                                ),
                                
                                

                                


                            ],
                        ),
                        
                      html.Div(
                          [
                              # Average of SellerRatings
                              dbc.Col(children=[html.H4("Seller's Ratings",
                                                        style={'padding-top': '0px', 'backgroundColor': '#FFFFFF'}),
                                                html.Div(round(df1.groupby('Seller')['SellerRatings'].mean().mean()),
                                                         style={'font-size': '34px', 'font-weight': '700',
                                                                'color': '#FFFFFF'}, )],
                                      width={"size": 1}),

                              # Average of products
                              dbc.Col(children=[html.H4("Seller's Products",
                                                        style={'padding-top': '0px', 'backgroundColor': '#FFFFFF'}),
                                                html.Div(round(df1.groupby('Seller')['Products'].mean().mean()),
                                                         style={'font-size': '34px', 'font-weight': '700',
                                                                'color': '#FFFFFF'}, )],
                                      width={"size": 1}),

                              # average of the followers
                              dbc.Col(children=[html.H4('# of Followers', style={'backgroundColor': '#FFFFFF'}),
                                                html.Div(round(df1.groupby('Seller')['Followers'].mean().mean()),
                                                         style={'font-size': '34px', 'font-weight': '700',
                                                                'color': '#FFFFFF'})],
                                      width={"size": 1}),

                              # average of the text
                              dbc.Col(children=[html.H4('Response Hour', style={'backgroundColor': '#FFFFFF'}),
                                                html.Div(round(Average_Res_Hour, 2),
                                                         style={'font-size': '34px', 'font-weight': '700',
                                                                'color': '#FFFFFF'})],
                                      width={"size": 1}),

                          ]
                                    ),  


                    ],
                ),
                         
                
            ],
        )

        #---- bottom ---

    ]
)



@app.callback(Output('ternary-map','figure'),
              [ Input('operator-select','value') ])
def toprightlineChart(AttributeName):

    data=[]

    x=df["Seller"]
    if AttributeName == "SellerRatings":
        y = df["SellerRatings"]
    elif AttributeName == "Products":
        y = df["Products"]
    elif AttributeName == "Followers":
        y = df["Followers"]
    elif AttributeName == "ResponseRate":
        # ResponseRate
        y = df["ResponseRate"]
    else:
        y=[]


    trace_close = go.Bar(
        x=x,
        y=y,
        name="11",
        marker=dict(
            line=dict(
                color='rgb(229, 152, 102)',
                width=1.5),
        )
    )

    data=[trace_close]

    layout = go.Layout(
        title="Comparison",
        barmode='group'
    )

    return {
        'data': data,
        'layout': layout
    }



if __name__ == "__main__":
    app.run_server(debug=True)
