# si206finalproject

####################################################
#####   Interactive A-List Celebrity Program    ####
####################################################
###########  Written By: William Minck  ############
####################################################

#--------------------------------------------------#
#-----------------Data Collection------------------#
#--------------------------------------------------#

In order to run this program, you must import the 
requests, BeautifulSoup, sqlite3, json, and plotly
modules. To set up a proper virtual environment, refer 
to the requirements.txt for specific details.

In order to run the OMBD API, Google Geocode API, and
plotly module, you must go to their respective websites
(http://www.omdbapi.com/apikey.aspx, 
 https://developers.google.com/maps/documentation/geocoding/get-api-key,
 https://plot.ly/python/getting-started/) and get API keys 
and a plotly username. You will then store these unique
codes in a file called secrets.py as follows:

OMDB_API_KEY = 'api key'
PLOTLY_USERNAME = 'plotly username'
PLOTLY_API_KEY = 'api key'
google_places_key = 'api key'

My data source for A-List Celebrity information came 
from Fandango.com/ More specifically, I used 
https://www.fandango.com/famous-actors-and-actresses/
to scrape the necessary data for each actor and actress
on the Fandango Top 50 Celebrity list.

From these links, I crawl into each person's personal
overview page. Each of those have the urls have the format 
http://www.fandango.com/people/<uniqueident>/overview/.

Through each of these unique urls, I scrape information
including the actor's name, birthday, hometown, and three most 
recent movies. Each actor's information is contained as a 
instance of the Talent class I define before data collection.

Additionally, I crawl to one extra link for each actor,
http://www.fandango.com/people/<uniqident>/film-credits,
in order to extract the total amount of movies he or she 
has appeared in.

Secondly, I make requests to the OMBD API in order to learn
more about the movies that each A-List celebrity have been in
recently. For each movie, I extract it's release year, rating, 
genre, and which A-List celebrities starred in it.

Lastly, in order to run my fourth visualization function, 
I was required to use the Google Geocode API in order to 
get the latitude and longitude coordinates for the hometown 
of each A-List celebrity.

#--------------------------------------------------#
#------------------Code Structure------------------#
#--------------------------------------------------#

My code works in three major phases: data collection, 
database insertion, and visualization.

For data collection, I wrote a function called
get_talent_data(), which scrapes and crawls through
Fandango.com/ in order to return a list of instances
of the Talent class.

Next, I write a function called init_db() which 
properly initializes my two tables, which are titled
Talent and Movies. The next function, insert_data(),
is where I fill my database with the data I collected.
Talent is relatively straight forward, as I was able to 
load each cell using the attributes declared within the 
Talent class beforehand. Movies was more complex to solve,
as I needed to establish a foreign key/primary key
relationship between the A-List actors in each movie and 
their Id's from the Talent table. To do this I made an
SQL statement to get the Names and Id's of each A-List actor
and accumulated them within a dictionary called
talent_names. With this dictionary, I was able to connect
each actor's name in the Movie table with their Id from the
Talent table.

Lastly, I wrote four separate functions for each visualization
option that the user's recieve in the interactive prompt:
graph_one(), graph_two(), graph_three(), and graph_four().
Within each function, I made SQL statements to pull the necessary
information from the database I've already initialized and filled.

For graph_one(), I pulled the Name and Total Appearances data using
an SQL statement from the Talent table with a limit. The limit ensures
that I collect the data for the 5 most popular actors and actresses.
I then use plotly syntax to generate a bar graph representing the total
movie appearances for the 5 most popular actors and actresses.

For graph_two(), I pulled the Hometown data using an SQL statement 
from the Talent table. I also wrote a dictionary pairing each state's name
with its postal abbreviation. I iterated through the cursor and got the
count for each state using dictionary accumulation. Then I sorted the 
dictionary by count value in descending order. I then use plotly syntax 
to generate a bar graph representing the 5 most common states that 
A-List celebrities are from.

For graph_three(), I pulled the Hometown data using an SQL statement 
from the Talent table. I wrote a dictionary pairing each region's
name with the respective state abbreviations within that US region. 
I also wrote a dictionary pairing each region's name initializing the 
count value at 0. I iterated through the cursor and got the
count for each region using dictionary accumulation. I then use plotly syntax 
to generate a pie chart representing the percentage breakdown of regions
where A-List celebrities are from.

For graph_four(), I pulled the Hometown data using an SQL statement 
from the Talent table. I iterated through the cursor and used each
hometown string in a request to the Google Geocode API. Parsing through
the resulting json data, I extract the latitude and longitude coordinates
for each A-List celebrity's hometown. I then use plotly syntax 
to generate a world map representing the specific place where each
A-List celebrity is from.

#--------------------------------------------------#
#--------------------User Guide--------------------#
#--------------------------------------------------#

To run the program, clone my git repository to a local repo. Then, navigate
to that repository in terminal and create the secrets.py file as
described before, then use the following command in your command line:

python3 final.py

Once the program is running, for an in depth description
of the commands for visualizations, please use the 'help' command.

Quit the program using 'exit'
