## Real Time Twitter Streamer 


## UPDATE - June 4, 2023 
*Twitter has removed [removed free read access to their APIs](https://developer.twitter.com/en), the free tier only allows you to post a limited number of tweets per month and you would need to upgrade to a paid tier in order to read incoming tweets. Additionally, there would likely need to be some tweaks required to connect to the new APIs as it stands to reason that they've made significant changes since I first created this repo about year or so ago. All that being said, I'm going to leave this repo up as it's still a good example of how to leverage Tweepy, in particular leveraging Tweepy in a solution where you have to override a lot of its methods to suit your needs. Meaning: no longer drag and drop into your solution or download and use immediately, but still usefull in the right circumstances. 


### Listener(s) for gathering tweets and performing natural language processing in real time. 

I built the initial versions of this based on simple curiousity around performing natural language processing on tweets, and what started out as basic Twitter scraper that would grab a sampling of all tweets turned into something that could be used to track sentiment in real time, gather research data, etc. 

The repo's contents are as follows:
* **Filter_Twitter_Listener_SQLite(FINAL).py:** a python script that will monitor twitter for the given set of keywords, run sentiment analysis and then write those tweets as they come in to a SQLite db. I used SQL because it was convenient, but you could drop in anything you'd like to store the tweets. 

* **Sample_TwitterListener(SQLite)_FINAL.py:** works similar to the above only it takes in a roughly 1% sampling of all tweets, rather than tweets that fit a particular keyword. The data flow for this one can get rather intense as it's not uncommon to to see anywhere from 12 - 20 tweets per second coming in. Also: don't be surprised if running this one for an extended period of time makes your computer run hot. 

* **Note:** I believe that the filtered tweet stream is limited to 1% of all tweets as well. 

* **secrets.py:** this is a file where you store your Twitter Developer API access credentials. The included one in this repo is empty, you just need to drop in the appropriate credentials after you create your developer's account. I'd advise to apply for an enhanced account, as there won't be any limits on streamed tweets. 

* **TwitterIngestion(FINAL).ipynb:** Jupyter notebook used to manage everything. Both listener scripts are pulled into the notebook as external classes. When you run either of the cells corresponding to each script, you will be promoted for # of keywords, keywords and # of tweets you'd like to retrieve depending on how you're gathering tweets. I also included some sample code for querying the SQLite DB, you can retrieve data by writing standard SQL queries within the pd.read_sql_query function. 

* **requirements.txt:** a file listing all the libraries used for this project. 

***Future enhancements are likely to include*** 
* A real time dashboard showing items like tweet volume and sentiment by keyword. My plan is to build dashboards with both Django and Streamlit, the former because that is what I'm more likely to encounter at work and the latter because it looks like a really elegant way to quickly stand up dashboards so it's a technology worth learning. 
* Better handling of connection issues, namely: I'd like the solution to pause when it receives a 420 or other error code and just wait for 5-10 minutes and then try to reconnect. 

### Updates: 
* 4/23/2022: small tweaks for usability and readability:
    * Added SQL queries for the sample DB instead of just having it
    for the filtered one
    * Added more details on the difference between the textblob and VADER sentiment analysis 
    * Split out each of the VADER sentiment analysis components instead of inserting the entire dictionary into a field 


#### Equipment used: 16" 2019 MacBook Pro, eight core Intel i9, 16GB 

#### Key Links:
* [Twitter Developer Site](https://developer.twitter.com/en)
* I leaned heavily on the [Tweepy documentation](https://docs.tweepy.org/en/stable/) 
* The [Tweepy source code Github](https://github.com/tweepy/tweepy) was an invaluable resource, as noted earlier customization requires overriding a lot of the methods, plus it was just easier to understand how everything worked from studying the source code. 