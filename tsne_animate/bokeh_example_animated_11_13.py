# imports
import pandas as pd
import numpy as np
import pickle

from sklearn.manifold import TSNE

from datetime import datetime, timedelta
import calendar

import bokeh.plotting as bp
from bokeh.plotting import save, reset_output, figure, show
from bokeh.models import HoverTool, ColumnDataSource, Slider, DateSlider, Button
from bokeh.layouts import layout, row, column, widgetbox
from bokeh.io import curdoc

# this was the document-topic matrix from nmf (sparse matrix)
with open('../nmf_doc_top_5_29.pkl', 'rb') as picklefile:
    nmf_doc_top = pickle.load(picklefile)

# this was a manually created topic list (a dict)
with open('../topic_list_5_29.pkl', 'rb') as picklefile2:
    topic_list = pickle.load(picklefile2)

# these were my documents (a dataframe)
with open('../new_reddit_topics.pkl', 'rb') as pick:
    submissions = pickle.load(pick)

# these were the t-sne coordinates (a dataframe?)   
with open('../tsne_nmf.pkl', 'rb') as pick2:
    tsne_nmf = pickle.load(pick2)
    
# convert dates from utc to standard date format and get a sorted list of unique dates
submissions['date'] = submissions['date_created'].apply(lambda x: x.date())
dates = sorted(list(set(submissions['date'])))

# get all the topic names into a list
topic_nm = list(topic_list.values())

# convert document topic matrix to a data frame
tfidfnmf_topics = pd.DataFrame(nmf_doc_top)
tfidfnmf_tmp = tfidfnmf_topics # not sure what this was for

# add some columns to base document-topic matrix (this is the main dataframe here)
tfidfnmf_topics['TopicNum'] = tfidfnmf_topics.idxmax(axis=1) # index of primary topic (max nmf weight)
tfidfnmf_topics['TopicWt'] = tfidfnmf_topics.iloc[:, :15].max(axis=1) # weight of primary topic
tfidfnmf_topics['PrimaryTopic'] = [topic_list[x] for x in tfidfnmf_topics['TopicNum']] # name of primary topic

# map colors to the topics and add to the main dataframe
colormap = np.array([
    "#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c",
    "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
    "#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f"
])
num_example = len(tfidfnmf_topics)
tfidfnmf_topics['color'] = colormap[tfidfnmf_topics['TopicNum']][:num_example]

# add t-sne coordinates to main dataframe
tfidfnmf_topics['tsne_x'] = tsne_nmf[:,0]
tfidfnmf_topics['tsne_y'] = tsne_nmf[:,1]

# get the top document for each of the primary topics (only used for placing labels on viz)
docs_by_topic = tfidfnmf_topics.groupby('PrimaryTopic')
topics_top_doc = docs_by_topic.idxmax()[['TopicWt']]
#topics_top_doc['DocText'] = [submissions.iloc[x]['text'] for x in topics_top_doc['TopicWt']]

# adds the full text of each document and the date to main dataframe
subm = submissions[['text', 'date']]
tfidfnmf_topics = pd.concat([tfidfnmf_topics, subm], axis=1)

# get relevant columns from main dataframe, store in a dict and ass to ColumnDataSource (bokeh plot data source)
tfidfnmf_dat = tfidfnmf_topics[['tsne_x', 'tsne_y', 'text', 'TopicWt', 'color', 'date']]
data = {}
for date in dates:
    df = tfidfnmf_dat[tfidfnmf_dat['date'] <= date]
    data[date] = df.to_dict('series')  
source = ColumnDataSource(data=data[dates[0]]) #here only those with the first unique date -- since this is a timelapse

# pass the data that will pop up when you hover over each point in the t-sne
hover = HoverTool(tooltips='''
    topic_wt: @TopicWt <br>
    text: <div style="width:350px">@text</div>
''')

# create figure object for t-sne plot, then add a bokeh circle plot (basically a scatter plot) 
p_nmf2 = figure(x_range=(-50, 50), y_range=(-30, 30),
                plot_width=1000, plot_height=700,
                     #title=title,
                tools=['pan','wheel_zoom','box_zoom','reset','previewsave', hover],
                x_axis_type=None, y_axis_type=None, min_border=1)
p_nmf2.circle(x='tsne_x', y='tsne_y', color='color', size=8, source=source)

# get coordinates for placing topic names on each cluster
topic_coord = np.empty((nmf_doc_top.shape[1], 2)) * np.nan
for topic in list(tfidfnmf_topics['PrimaryTopic']):
    if np.isnan(topic_coord).any():
        doc_index = int(topics_top_doc.loc[topic]['TopicWt'])
        top_index = [k for k, v in topic_list.items() if v == topic]
        topic_coord[top_index] = tsne_nmf[doc_index]

# put the labels onto the plot
for i in range(len(topic_list.items())):
    p_nmf2.text(topic_coord[i, 0], topic_coord[i, 1], [topic_nm[i]])

# this animates the timelapse (when the slider moves)
def animate_update():
    date = slider.value + timedelta(days=1)
    if date > dates[-1]:
        date = dates[0]
    slider.value = date

# this updates the slider (by date)
def slider_update(attrname, old, new):
    new = slider.value
    source.data = data[new]
    #source.data = {k: data[k] for k in data.keys() if k <= slider.value}

# create the slider object and what happens when it changes
slider = DateSlider(start=dates[0], end=dates[-1], value=dates[0], step=1, title='Date')
slider.on_change('value', slider_update)

# this animates the timelapse (when the button gets pushed)
callback_id = None
def animate():
    global callback_id
    if button.label == '► Play':
        button.label = '❚❚ Pause'
        callback_id = curdoc().add_periodic_callback(animate_update, 120)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(animate_update)

# create the button object and what happens when it gets clicked
button = Button(label='► Play', width=60)
button.on_click(animate)

# add plot, slider, and button to layout and "publish"
layout = layout([p_nmf2, [slider, button]], width=800)
curdoc().add_root(layout)