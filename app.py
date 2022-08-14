import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])
mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')
gss_clean = gss_clean.replace({'sex':{'female':'Female','male':'Male'}})

markdown_text = '''
The most recent [2020 Census Bureau data](https://www.census.gov/data/tables/time-series/demo/income-poverty/cps-pinc/pinc-05.html) showed that women earned 83 cents for every $1 earned by men. This dashboard provides descriptive statistics on sex differences using data from the 2018 General Social Survey. 

The [2018 General Social Survey](https://gss.norc.org/About-The-GSS) is a personal-interview survey conducted by the National Opinion Research Center at the University of Chicago. For the 2018 survey, 2,348 interviews were conducted via full probability-sampling, and the median length of the interviews was about one and a half hours. Demographic data and data related to one's profession were collected. For the purpose of this dashboard a subset of variables were selected, one of them being job prestige. Job prestige was measured by having respondents rank different jobs in a hierarchical ladder and aggregating the rankings. The full description of their methodology can be found in their [report](http://gss.norc.org/Documents/reports/methodological-reports/MR122%20Occupational%20Prestige.pdf). Other variables visualized in this dashboard inclue annual income, sex, years of education and socioeconomic index.  
'''

table_draft = gss_clean.groupby('sex').agg({'job_prestige':'mean','income':'mean','socioeconomic_index':'mean','education':'mean'}).reset_index()
table_draft = table_draft.rename({'job_prestige':'Average Job Prestige',
                                 'income':'Average Income',
                                 'socioeconomic_index':'Average Socioeconomic Index',
                                 'education':"Average Education",
                                  'sex': "Sex"
                                 },axis=1)
table = ff.create_table(round(table_draft,2))

fig2 = px.scatter(gss_clean, x='job_prestige', y='income', 
                 color = 'sex', 
                 trendline='ols',
                 height=600, width=700,
                 labels={'job_prestige':'Job Prestige', 
                        'income':'Annual Income'},
                 hover_data=['education','socioeconomic_index'])


fig3 = px.box(gss_clean, x='income', y = 'sex', color = 'sex',
                   labels={'income':'Annual Income', 'sex':''})
fig3.update_layout(showlegend=False)

fig4 = px.box(gss_clean, x='job_prestige', y = 'sex', color = 'sex',
                   labels={'job_prestige':'Job Prestige', 'sex':''})
fig4.update_layout(showlegend=False)

new = gss_clean[['income','sex','job_prestige']]
new['prestige_cat'] = pd.cut(gss_clean.job_prestige,6,labels=('very low prestige','low prestige','kinda low prestige','kinda prestige','high prestige','very high prestige'))
new = new.dropna()
fig5 = px.box(new, x='income', y='sex', color='sex', 
             facet_col='prestige_cat',facet_col_wrap=2,
             width=900,
             height=600,
             color_discrete_map={'female':'green','male':'purple'},
             labels={'income':'Annual Income', 'sex':''})
fig5.update_layout(showlegend=False)
fig5.for_each_annotation(lambda a: a.update(text=a.text.replace("prestige_cat=", "")))


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.LUX])

tab1 = dbc.Tab([dcc.Graph(figure=fig2)], label="Scatterplot")
tab2 = dbc.Tab([dcc.Graph(figure=fig5)], label="Boxplot by  Job Prestige Categories")
tabs = dbc.Tabs([tab1, tab2])

app.layout = html.Div(
    [
        html.H1("Exploring the 2018 General Social Survey"),
        
        dcc.Markdown(children = markdown_text),
        
        html.H2("Mean Income, Job Prestige, Socioeconomic Index, and Years of Education by Sex"),
        
        dcc.Graph(figure=table),
        
        html.H2("Responses to Survey Questions"),        
                
        html.Div([
            dbc.Label("Select Question"),
        dcc.Dropdown(id = 'dropdown',
                     options = [{'label': j, 'value': i} for i,j  in zip(gss_clean[['satjob','relationship','male_breadwinner','men_bettersuited', 'child_suffer','men_overwork']].columns, 
                                          ["On the whole, how satisfied are you with the work you do?",
                                          "A working mother can establish just as warm and secure a relationship with her children as a mother who does not work.",
                                          "It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family.",
                                           "Most men are better suited emotionally for politics than are most women.",
                                          "A preschool child is likely to suffer if his or her mother works.",
                                          "Family life often suffers because men concentrate too much on their work."])],
                    value="satjob"),
            dbc.Label("Select Grouping Variable"),
            dcc.Dropdown(id = 'dropdown2',
                     options = [{'label': i, 'value': i}   
                                for i in gss_clean[['sex','region','education']].columns],
                        value='sex'),
        dcc.Graph(id='displaybar')],style = {'width':'50%', 'float':'center'}),
        
        html.Div([
            
            html.H2("Income Distribution by Sex"),
            
            dcc.Graph(figure=fig3)
            
        ], style = {'width':'48%', 'float':'left'}),
        html.Div([
            
            html.H2("Job Prestige by Sex"),
            
            dcc.Graph(figure=fig4)
            
        ], style = {'width':'48%', 'float':'right'}),
        
        html.H2("Relationship Between Income and Job Prestige By Sex"),
        html.Div([tabs],style={'float':'left'})
    ])

@app.callback(Output(component_id = 'displaybar', component_property = 'figure'),
              [Input(component_id = 'dropdown', component_property = 'value'),
               Input(component_id = 'dropdown2', component_property = 'value')]) 
def createbar(loc,group):
    if f"{loc}"=='satjob':
        tab = pd.crosstab(gss_clean[f"{group}"],gss_clean[f"{loc}"]).reset_index()
        long = pd.melt(tab,id_vars=[f"{group}"],
                  value_vars=['a little dissat','mod. satisfied','very dissatisfied',
                              'very satisfied']).rename({f"{loc}": 'Responses'},axis=1)
        long['Responses'] =  long.Responses.astype('category').cat.reorder_categories(['very satisfied',
                                                                                                 'mod. satisfied',
                                                                                                 'a little dissat',
                                                                                                 'very dissatisfied'])
        long = long.sort_values('Responses') # need to sort by Responses so that in the graph they are listed in the order I want

        fig = px.bar(long, x=f"{group}",y='value',color='Responses',barmode='group',
           labels={'value':'Counts'},
                 height=600, width = 800
          )
    else:
        tab = pd.crosstab(gss_clean[f"{group}"],gss_clean[f"{loc}"]).reset_index()
        long = pd.melt(tab,id_vars=[f"{group}"],
                  value_vars=['agree','disagree','strongly agree','strongly disagree']).rename({f"{loc}": 'Responses'},axis=1)
        long['Responses'] =  long.Responses.astype('category').cat.reorder_categories(['strongly agree',
                                                                                                 'agree',
                                                                                                 'disagree',
                                                                                                 'strongly disagree'])
        long = long.sort_values('Responses') # need to sort by Responses so that in the graph they are listed in the order I want

        fig = px.bar(long, x=f"{group}",y='value',color='Responses',barmode='group',
           labels={'value':'Counts'},
                 height=600, width = 800
          )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)

