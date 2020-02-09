# Using Data to Find the Most Brutal Cannibal Corpse Song

A repository containing code for an analytics project in Python to identify the most brutal song based on audio features and analysis of the lyrics. I have written a [blogpost on Medium](https://medium.com/p/bf318d0b3ef4/) about it. That post gives a nice overview over the approach and the result. The jupyter notebooks stored here provide all the code and go a little deeper in explaining and analyzing certain aspects of the project.

In case you don't know what Cannibal Corpse is - shame on you! Follow this [link](https://en.wikipedia.org/wiki/Cannibal_Corpse), please.

## Introduction to project and code

The analysis was performed in Python. Audio related features were requested from the Spotify API (using the `spotipy` library) and lyrics scraped from the genius website (using a mixed approach of API requests and web-scraping with the `beautifulsoup4` library).

The analysis is broken up in **two parts / jupyter notebooks**:

1) The first contains the requesting of audio features from the Spotify API and the calculation of a "Sonic Brutality Index" for each song. It also contains an appendix comparing Cannibal Corpse's 'brutality' to that of Cannabis Corpse (of interest for Death Metal nerds only).
2) The second contains the scraping of the lyrics from genius.com and the calculation of a "Lyrical Brutality Index", and then of the final "Total Brutality Index" by combining _sbi_ and _lbi_.

Each notebook has an Appendix with some extra analyis. If you are into Cannibal Corpse - have a look ;-).

## Install

This project requires **Python 3.7** and the following Python libraries installed:

- [NumPy](http://www.numpy.org/)
- [Pandas](http://pandas.pydata.org)
- [matplotlib](http://matplotlib.org/)
- [seaborn](http://seaborn.org)
- [scikit-learn](http://scikit-learn.org/stable/)
- [tqdm](https://pypi.org/project/tqdm/)
- [spotipy](https://pypi.org/project/spotipy/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- [nltk](http://www.nltk.org/)

You will need to register for the Spotify and Genius APIs to work with your own credentials. I'll keep mine secret.
And you will also need to have software installed to run and execute an [Jupyter Notebook](http://ipython.org/notebook.html)

`environment.yml` and `requirements.text` are provided.

## Acknowledgements and Thanks

- Evan Oppenheimer for inspiring me with his [blogpost on finding the angriest Death Grip song](https://towardsdatascience.com/angriest-death-grips-data-anger-502168c1c2f0) (in R)
- Charlie Tompson for inspiring Evan in the first place with this [blogpost on finding sad Radiohead songs]( https://www.rcharlie.com/post/fitter-happier/) (in R too)
- Saif Mohammad for publishing [The NRC Valence, Arousal, and Dominance Lexicon](http://saifmohammad.com/WebPages/nrc-vad.html)
- Everybody contributing to the [spotipy library](https://spotipy.readthedocs.io/en/latest/)
- Chris Hyland for this really helpful [Blogpost on scraping song lyrics](https://chrishyland.github.io/scraping-from-genius/)
- Spotify for providing a very well documented and complete [Web API](https://developer.spotify.com/documentation/web-api/reference/)
- Genius for providing a nice [Web API](https://docs.genius.com/#/getting-started-h1) too
- All the nerds contributing to Genius


**Project End Date:** Feb 2020
