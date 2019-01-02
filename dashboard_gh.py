#Import modules
import pandas as pd
import numpy as np
from bokeh.io import curdoc, output_file, show
from bokeh.models import ColumnDataSource, CategoricalColorMapper, Slider, HoverTool, Select
from bokeh.plotting import figure
from bokeh.palettes import Spectral6, YlOrBr #@UnresolvedImport
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Panel, Tabs
from bokeh.transform import cumsum

df = pd.read_csv('..\datasets\StudentsPerformance.csv')

#Pie charts for the catogorical varibles
def pie_chart(attr, old, new):
    d = df
    value = pie_select.value
    dic = {'label': [], 'ang': [], 'colors': [], 'perc': []}
    c = list(d[value].unique())
    for i, data in d.groupby([pie_select.value]):
        dic['label'].append(i)
        dic['ang'].append(data.shape[0] / d.shape[0] * 360)
        dic['perc'].append(round((data.shape[0] / d.shape[0]) * 100, 0))
        dic['colors'].append(YlOrBr[9][c.index(i)])
    source.data = dic
    pie.title.text = value

pie_select = Select(
    options=['gender','race/ethnicity','parental level of education','lunch','test preparation course'],
    value='gender',
    title='Select data'
)


d = df
dic = {'label': [], 'ang': [], 'colors': [], 'perc': []}
c = list(d['gender'].unique())
for i,data in d.groupby(['gender']):
    dic['label'].append(i)
    dic['ang'].append(data.shape[0]/d.shape[0] * 360)
    dic['perc'].append(round((data.shape[0]/d.shape[0])*100, 0))
    dic['colors'].append(YlOrBr[9][c.index(i)])
source = ColumnDataSource(data=dic)

pie = figure(title='gender', tools="hover", tooltips=[('label', '@label'), ('percentage', '@perc')])
pie.wedge(x=0, y=1, radius=0.5, start_angle_units='deg', end_angle_units='deg',
           start_angle=cumsum('ang', include_zero=True), end_angle=cumsum('ang'),
           legend='label', source=source, color='colors', line_color='white')


pie_select.on_change('value', pie_chart)
layout1 = row(widgetbox(pie_select), pie)

#Histogram for the scores
def update_hist(attr, old, new):
    df2 = df

    hist, edges = np.histogram(df2[scores_select.value], density=True, bins=100)
    mu = df2[scores_select.value].mean()
    sigma = df2[scores_select.value].std()
    x = np.linspace(df2[scores_select.value].min(), df2[scores_select.value].max(), df2[scores_select.value].shape[0])
    pdf = 1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(-(x - mu) ** 2 / (2 * sigma ** 2))

    source_h.data = {'hist': hist, 'edges1': edges[:-1], 'edges2': edges[1:]}
    source_c.data = {'x': x, 'pdf': pdf}
    histogram.title.text = scores_select.value


hist, edges = np.histogram(df['math score'], density=True, bins=100)
mu = df['math score'].mean()
sigma = df['math score'].std()
x = np.linspace(df['math score'].min(), df['math score'].max(), df['math score'].shape[0])
pdf = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(x-mu)**2 / (2*sigma**2))
source_h = ColumnDataSource(data={'hist': hist, 'edges1': edges[:-1], 'edges2': edges[1:]})
source_c = ColumnDataSource(data={'x':x,'pdf':pdf})

histogram = figure(title='math score', tools='', background_fill_color="#fafafa")
histogram.quad(top='hist', bottom=0, left='edges1', right='edges2',fill_color="navy",
       line_color="white", alpha=0.5, source=source_h)
histogram.circle('x', 'pdf', line_color="#ff8888", line_width=4, alpha=0.7, legend="PDF",source=source_c)

scores_select = Select(
    options=['math score', 'reading score', 'writing score'],
    value='math score',
    title='Scores'
)

scores_select.on_change('value', update_hist)

layout2 = row(widgetbox(scores_select), histogram)

#Scatter charts
def update_scatter(attr, old, new):
    source_s.data = {'x': df[scores1_select.value], 'y': df[scores2_select.value]}
    scatter.title.text(str(scores1_select)+' vs '+str(scores2_select.value))


source_s = ColumnDataSource(data={'x': df['math score'], 'y': df['reading score']})
scatter = figure(title='Math Score vs Reading Score', tools='', background_fill_color="#fafafa")
scatter.circle('x', 'y', line_color="#ff8888", line_width=4, alpha=0.7, source=source_s)

scores1_select = Select(
    options=['math score', 'reading score', 'writing score'],
    value='math score',
    title='Scores'
)

scores2_select = Select(
    options=['math score', 'reading score', 'writing score'],
    value='reading score',
    title='Scores'
)

scores1_select.on_change('value', update_scatter)
scores2_select.on_change('value', update_scatter)

layout3 = row(widgetbox(scores1_select, scores2_select), scatter)

tab1 = Panel(child=layout1, title='Pie Chart')
tab2 = Panel(child=layout2, title='Histogram - KDE')
tab3 = Panel(child=layout3, title='Scatter Chart')

layoutFinal = Tabs(tabs=[tab1, tab2, tab3])

curdoc().add_root(layoutFinal)
curdoc().title = 'StudentsPerformance'