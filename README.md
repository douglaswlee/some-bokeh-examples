# some-bokeh-examples

Basic repo for some example viz done in Bokeh. Remember that there are plentiful [examples](https://bokeh.pydata.org/en/latest/docs/gallery.html#gallery) from the main bokeh page to use as reference.

There are two folders here at the moment:
* **tsne_basic**, which has the code (`bokeh_example_11_08.py`) for a basic t-SNE plot in bokeh following the procedure described [here](https://shuaiw.github.io/2016/12/22/topic-modeling-and-tsne-visualzation.html)
* **tsne_animate**, which has the code (`bokeh_example_animate_11_13.py`) for basically the same t-SNE plot but in a timelapse animation

There are also a bunch of pickle files that are described in the two .py files above. You may replace these with analogs from your own text data (of course for the "animated" version you will need text data that has dates and times).

Fork all of this and preserve the file structure. Here's an example of the command you can run -- in the relevant folder of course -- to see the truly incredible viz that is produced:

`bokeh serve --show bokeh_example_11_08.py`
