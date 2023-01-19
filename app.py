import dash
from dash import html, dash_table, dcc, callback
import dash_bootstrap_components as dbc
import json
import pandas as pd
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import os

dict_abreviaturas_organos = {
    'Consejeria': 'C.',
     'Instituto': 'Inst.',
     'Delegacion': 'Del.',
     'Provincial': 'Prov.',
     'Secretaria': 'Secr.',
     'General': 'Gral.',
     'Generales': 'Gral.',
     'Direccion': 'Dir.',
     'Hospital': 'Hsp.',
     'Hospitalario': 'Hsp.',
     'Asistencia': 'Asst.',
     'Sanitaria': 'Sanit.',
     'Gerencia': 'Gcia.',
     'Integrada': 'Int.',
     'Atencion': 'Aten.',
     'Especializada': 'Esp.',
     'Urgencias': 'Urg.',
     'Emergencias': 'Emerg.',
     'Universitario': 'Univ.',
     'Complejo': 'Compl.',
     'Educacion': 'Ed.',
     'Cultura': 'Cult.',
     'Deportes': 'Dep.',
     'Juventud': 'Juv.',
     'Viceconsejeria': 'Vc.',
     'Agricultura': 'Agr.',
     'Desarrollo': 'Desa.',
     'Agroalimentario': 'Agroa.',
     'Investigacion': 'Invest.',
     'Regional': 'Reg.',
     'Universidad': 'Univ.',
     'Residencia': 'Resi.',
     'Residencial': 'Resi.',
     'Centro': 'Ctro.',
     'Ocupacional': 'Ocupac.',
     'Asistidos': 'Asist',
     'Junta': 'J.',
     'Comunidades': 'C.',
     'Hacienda': 'Hda.',
     'Fundacion': 'Fund.',
     'Planificacion': 'Planif.',
     'Administraciones': 'Admin.',
     'Administracion': 'Admin.',
     'Ambiente': 'Amb.',
     'Publicas': 'Pub.',
     'Economia, Empresas y Empleo': 'Eco. Empr. y Empl.',
     'Autonomos': 'Auton.',
     'Promocion': 'Prom.',
     'Exterior': 'Ext.',
     'Delegado': 'Del.',
     'Delegada': 'Del.',
     'Jefatura': 'Jef.',
     'Intervención': 'Interv.',
     'Servicio': 'Serv.',
     'Superior': 'Sup.',
     'Adjunto': 'Adj.',
     'Sociedad': 'Soc.',
     'Castilla-La Mancha': 'C. L. M.',
     'Castilla La Mancha': 'C. L. M.',
     ' en ': ' ',
     ' de ': ' ',
     ' la ': ' ',
     ' el ': ' ',
     ' y ': ' ',
     ' del ': ' ',
     '-': ''
}

path_file = '../0 Datos/0 RAW/web-catalogo_procedimientos_y_tramites_05-12-2022.xlsx'
file = pd.ExcelFile(path_file)
# pd.read_excel(,sheet_name=1)

df_tram = pd.read_excel(path_file, sheet_name = 'Total')
df_tram.columns = [x.strip() for x in df_tram.columns]
df_tram['PLAZO_N'] = df_tram.PLAZO.str.extract(r'(^\d{1})')

df_tram['CONSEJERIA'] = df_tram.CONSEJERIA.str.title()
for i,j in dict_abreviaturas_organos.items():
    df_tram['CONSEJERIA'] = df_tram['CONSEJERIA'].str.replace(i,j)

df_tram['ÓRGANO'] = df_tram['ÓRGANO'].str.title()
for i,j in dict_abreviaturas_organos.items():
    df_tram['ÓRGANO'] = df_tram['ÓRGANO'].str.replace(i,j)

all_cats = ['DEPTO','ÓRGANO','SILENCIO','PRESENCIAL','ONLINE','O12','VUDS']
options_cats = [{'label':i.title(),'value':i,'disabled':False} for i in all_cats]
# Inicialización de la app.
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
server = app.server



radio_cats = dcc.Checklist(
	id = 'radio_cats',
    options=options_cats,
    value=['PRESENCIAL'],
    inline=True,
    labelStyle={'display': 'block'},
    style={'overflow':'auto'}
)

bar_chart = dcc.Graph(id="bar_chart")

checkpoint_1 = dcc.Store(id='checkpoint_data_1')

pie_1 = dcc.Graph(id="pie_chart_1")

pie_2 = dcc.Graph(id="pie_chart_2") 

tabla_display = html.Div(
    dash_table.DataTable(id='tabla_display',
                         columns=[{"name": i, "id": i, "deletable": True} for i in df_tram.columns],
                         page_size=10,
                         editable=True,
                         cell_selectable=True,
                         filter_action="native",
                         sort_action="native",
                         style_table={"overflowX": "auto"},
                         row_selectable="multi"),
    className="dbc-row-selectable",
    )


app.layout = html.Div([
    dbc.Row([
        dbc.Col([html.Img(src="assets/crid.png", style={'width':'100%'})], width=2),
        dbc.Col([html.Div("Exploración trámites", style={'fontSize':50, 'textAlign':'center'})], width=10)
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([radio_cats], width = 2),
        dbc.Col([bar_chart], width = 10),
        checkpoint_1

    ]),
    dbc.Row([
        dbc.Col([pie_1], width = 6),
        dbc.Col([pie_2], width = 6),

    ]),
    dbc.Row([tabla_display])
])

@app.callback(
    dash.dependencies.Output('bar_chart','figure'),
    [dash.dependencies.Input('radio_cats','value')]
)
def update_bar(radio_categ):
    list_cols = ['CONSEJERIA']+radio_categ
    data_plot = df_tram.groupby(list_cols).size().to_frame().reset_index().sort_values(by=[0], ascending=False)
    pal_cons = sns.cubehelix_palette(data_plot.shape[0], rot=-.25, light=.7).as_hex()

    fig_bar = go.Figure()

    if len(radio_categ) > 0:
        i = 0
        # for categ_col in radio_categ:
        #     for categ in data_plot[categ_col].unique():
        df_combo = data_plot[radio_categ].drop_duplicates()
        cats = [j for i,j in df_combo.iterrows()]
        pal_categ = sns.cubehelix_palette(df_combo.shape[0], rot=-.25, light=.7).as_hex()

        for cat in cats:
            data = data_plot.loc[(data_plot[radio_categ] == pd.Series(dict(zip(radio_categ,cat.values)))).all(axis=1)]
        #     data = data_plot.loc[data_plot[categ_col]==categ]
            fig_bar.add_trace(go.Bar(
                x=data.CONSEJERIA,
                y=data[0],
                name=f'{radio_categ}: {cat.values}',
                marker_color=pal_categ[i],
                text=data[0].astype(str),
                customdata=["CONSEJERIA"],
                textposition='inside',
                hovertemplate="<br>".join([
                                "%{x} ",
                                "%{y} Trámites"
                                ])
            ))
            fig_bar.update_yaxes(showticklabels=True)#, range = [0,data_plot[0].max()*1.4])
            fig_bar.update_layout(
                barmode='stack',
                title='Distribución de trámites',
                xaxis={'dtick':'M1'},    
                yaxis={'side': 'left'},
                showlegend=False
            )
            i+=1
    else:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=data_plot.CONSEJERIA,
            y=data_plot[0],
            name='Distribución de trámites por consejería',
            marker=dict(color=pal_cons),
            text=data_plot[0].astype(str),
            customdata=["CONSEJERIA"],
            textposition='inside',
            hovertemplate="<br>".join([
                            "%{x} ",
                            "%{y} Trámites"
                            ])
        ))
        fig_bar.update_yaxes(showticklabels=True)#, range = [0,data_plot[0].max()*1.4])
        fig_bar.update_layout(
            title='Distribución de trámites',
            xaxis={'dtick':'M1'},    
            yaxis={'side': 'left'},
            showlegend=False
        )
    return fig_bar
        
        
@callback(
    dash.dependencies.Output("checkpoint_data_1","data"),
    [dash.dependencies.Input("bar_chart", "clickData")]
)
def update_data_1(click):
    data = df_tram.copy()
    if click:
        filtro = click["points"][0]["label"]
        print(filtro)
        return data.loc[data.CONSEJERIA==filtro].to_json(orient='split')
        
@callback(
    dash.dependencies.Output('pie_chart_1','figure'),
    dash.dependencies.Output('pie_chart_2','figure'),
    dash.dependencies.Output('tabla_display','data'),
    [dash.dependencies.Input('checkpoint_data_1','data')]
)
def update_pies(data):
    data_pie = pd.read_json(data,orient='split')
    
    data_pie_1 = data_pie.groupby('ÓRGANO').size().reset_index().rename(columns={0:'Trámites'})
    data_pie_2 = data_pie.groupby('SILENCIO').size().reset_index().rename(columns={0:'Trámites'})

    pal1 = sns.cubehelix_palette(data_pie_1.shape[0], rot=-.25, light=.7).as_hex()
    pal2 = sns.cubehelix_palette(data_pie_2.shape[0], rot=-.25, light=.7).as_hex()

    fig_1 = go.Figure()
    fig_1.add_trace(go.Pie(
        labels=data_pie_1['ÓRGANO'],
        values=data_pie_1['Trámites'],
        hole=0.25,
        marker=dict(colors=pal1, line=dict(color='#000000', width=2)),textinfo='label+percent'))
    fig_1.update_layout(showlegend=False)
    
    fig_2 = go.Figure()
    fig_2.add_trace(go.Pie(
        labels=data_pie_2['SILENCIO'],
        values=data_pie_2['Trámites'],
        hole=0.25,
        marker=dict(colors=pal2, line=dict(color='#000000', width=2)),textinfo='label+percent'))
    fig_2.update_layout(showlegend=False)        
    return fig_1, fig_2, data_pie.to_dict('records')





if __name__ == "__main__":
    app.run(debug=True)