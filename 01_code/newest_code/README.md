## Data-Set Description

### 1. Disclaimer
The data below has been provided by the Priesemann group and may only be used for research purposes.
Any sharing of this data or dervied data with 3rd parties requires the argeement of the Priesemann group.

### 2. Overview
This dataset focusses on data from english public telegram channels and the sharing behaviour of different URLs by different channels.
There are 3 entities that we care about:
- URLs i.e. weblinks that were shared by some channel in the data-set
- Channels (public on Telegram) that are posting content
- Shares of a certain url in a certain channel
All three different objects are stored in this data "package". Below is explained how.

### 3. Data Format
All dataframes are stores as .parquet format and should be readable using the python library "pandas".

#### 3.1 URL Data
The url data is split into two dataframes. One dataframe `url.data.parquet` (3GB) contains some general data for each of the roughly 60 Million different shared URLs in our english Telegram data. Additionally for "popular" urls - that is URLs that were posted more than 10 times in the data-set, we provide the second dataframe `url.text.parquet` which contains text samples for the most viewed or forwarded messages that contained a certain URL. Additionally this datafram contains also how many views and forwards messages containing this URL got within Telegram (at least our dataset).

##### 3.1.1 The `url.data.parquet` DataFrame - General Data
The dataframe contains one row for each url and specifies some general properties like
- index a unique index 0..60789533 ref. to each individual url
- the url string
- the domain
- messages: how many messages in the data contained this url
- chats: how many different chats posted the url
Then it also contains a lot of information about the spreading dynamics of this url in the Telegram network (i.e. how did the temporal distribution of the posts look like). The posting activity is clustered together into avalanches (i.e.) bursts of activity. 
- avalanches: how many avalanches (i.e. indivdual bursts of spreading) were there for this url
- mean_avalanche_size: how many messages (that reference this url) did one avalanche contain on average
- top_avalanche_size: what size did the largest avalanche have (this can get quite large)
- virality: A number between 0 and 1 that measures how "bursty" the spread of the url was. virality=1 if it spread in one large continous burst, virality=0 if it spread over time in many small independent bursts
- top_shares_X: highest number of messages containing this url were posted within a time window of X. (X=1hour,6hours,1day,3days,14days)
- first/last_share_date: timestamp of first and last shared message with this url

##### 3.1.2 The `url.text.parquet` - Text Data For Popular URLs
For popular urls, that is URLs which are shared in more than 10 different messages, there is additional data available. This data mainly contains some information about the number of views/forwards these urls got. Furthermore, the file contains text samples from the 3 most viewed and forwarded messages. The DataFrame is structured as follows:
- url: the string of the corresponding url
- msg: the number of messages that contained this url
- mean_views: the average view number of such a message
- mean_forwards: the average forward number of such a message
- top_X_fwds_(id,text,fwds) where X=1,2,3: The 3 most forwarded messages that contain this url, their id (database intern), their text and the number of forwards
- top_X_views_(id,text,fwds) where X=1,2,3: The 3 most viewed messages that contain this url, their id (database intern), their text and the number of views
Note in the top viewed/forwarded messages there can be (and often is) overlap.

#### 3.2 Chat Data
Public Channels and Group-Chats in Telegram that we crawled are called "chats". Each (english speaking) chat we found is contained in the `chats.parquet` data frame. This dataframe provides one row for each of these chats with some information. This is as follows:
- id: a unique index 0..XXX ref. to each individual chat
- db_index: a unique index of this chat in our database (in here for consistency reasons)
- the chat name
- type: The type of the chat (Channel, Group Chat, .. see Telegram Doc.)
- member_count: How many people are following this chat / or are members (might not be available for many channels - should not be used)
- description: The self description string of the channel
- messages: Number of all messages posted in this chat
- views: The total views all messages from this chat have
- forwards: The total number of forwards all messsages from this channel have generated
- age: The timestamp of the oldest known message from this chat

### 3.3 Sharing Data
The large SPARSE matrix `chat_url_shares.npz` stores how many messages each channel has posted that contain a certain URL. This means the matrix has shape (chat.id x url.index)  that stores for each pair of chat and url how many times a certain chat posted this url.
