import requests
import sqlite3
import json
import secrets
from bs4 import BeautifulSoup
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

plotly.tools.set_credentials_file(username= secrets.PLOTLY_USERNAME, api_key= secrets.PLOTLY_API_KEY)

CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def get_unique_key(url):
  return url

def make_request_using_cache(url, params={}):
    unique_ident = get_unique_key(url)

    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]

    else:
        # Make the request and cache the new data
        resp = requests.get(url, params)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

class Talent():
    def __init__(self, nm, dob, pob, m1, m2, m3, total):
        self.name = nm
        self.birthdate = dob
        self.birthplace = pob
        self.movie1 = m1
        self.movie2 = m2
        self.movie3 = m3
        self.total = total

    def __str__(self):
        return "{} was born on {}, in {}, and has most recently appeared in {}, {}, and {}.".format(self.name, self.birthdate, self.birthplace, self.movie1, self.movie2, self.movie3)


def get_talent_info():
    talent_urls = []
    baseurl = 'https://www.fandango.com/famous-actors-and-actresses'
    result = make_request_using_cache(baseurl)
    soup = BeautifulSoup(result, 'html.parser')
    content = soup.find(class_="topperformers-table")
    profile_soup = soup.find_all('a', href=True)
    for talent in profile_soup:
        if talent['href'][24:30] == 'people':
            if talent['href'] not in talent_urls:
                talent_urls.append(talent['href'])

    talent_instances = []
    for url in talent_urls:
        result = make_request_using_cache(url)
        soup = BeautifulSoup(result, 'html.parser')
        name = soup.find_all(class_='pop-header--headline-link')[0].text
        if len(soup.find_all(class_='pop-headshot--birthdate')) > 0:
            bday = soup.find_all(class_='pop-headshot--birthdate')[0].text.split(':')[-1]
        else:
            bday = 'Unknown'
        if len(soup.find_all(class_='pop-headshot--birthplace')) > 0:
            bplace = soup.find_all(class_='pop-headshot--birthplace')[0].text.split(':')[-1].strip()
        else:
            bplace = 'Unknown'
        most_recent_movie = soup.find_all(class_='heading-style-1 heading-size-s heading__movie-carousel')[0].text
        second_recent_movie = soup.find_all(class_='heading-style-1 heading-size-s heading__movie-carousel')[1].text
        third_recent_movie = soup.find_all(class_='heading-style-1 heading-size-s heading__movie-carousel')[2].text

        extra = make_request_using_cache(url[:-9] + '/film-credits')
        second_soup = BeautifulSoup(extra, 'html.parser')
        table = second_soup.find('table', {'class': 'pop-tabular--table'})
        total_movies = len(table.find_all('tr')) - 1

        talent_instances.append(Talent(nm=name,dob=bday,pob=bplace,m1=most_recent_movie,m2=second_recent_movie,m3=third_recent_movie,total=total_movies))

    return talent_instances

DBNAME = 'movies.db'

try:
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
except:
    print("Error occurred connecting to database")

def init_db():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Database creation failed")

    statement = "DROP TABLE IF EXISTS 'Talent'"
    cur.execute(statement)
    statement = "DROP TABLE IF EXISTS 'Movies'"
    cur.execute(statement)
    statement = '''
            CREATE TABLE 'Talent' (
                    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
                    'Name' TEXT NOT NULL,
                    'Birthday' TEXT NOT NULL,
                    'Hometown' TEXT NOT NULL,
                    'Most Recent Movie' TEXT NOT NULL,
                    'Second Recent Movie' TEXT NOT NULL,
                    'Third Recent Movie' TEXT NOT NULL,
                    'Total Movie Appearances' INTEGER
            );
        '''
    cur.execute(statement)
    statement = '''
            CREATE TABLE 'Movies' (
                    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
                    'Title' TEXT NOT NULL,
                    'Year' TEXT NOT NULL,
                    'Rating' TEXT NOT NULL,
                    'Genre' TEXT NOT NULL,
                    'Talent' TEXT NOT NULL,
                    'TalentId' INTEGER,
                    'Talent(Second)' TEXT,
                    'Talent(Second)Id' INTEGER,
                    'Talent(Third)' TEXT,
                    'Talent(Third)Id' INTEGER
            );
        '''
    cur.execute(statement)
    conn.commit()
    conn.close()

def insert_data():
    talent_list = get_talent_info()
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Database creation failed")


    for talent in talent_list:
        talent_insertion = (None, talent.name, talent.birthdate,
                            talent.birthplace, talent.movie1, talent.movie2,
                            talent.movie3, talent.total)
        statement = "INSERT INTO 'Talent' "
        statement += "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        cur.execute(statement, talent_insertion)

    talent_names = {}
    statement = "SELECT Id, Name FROM Talent"
    cur.execute(statement)
    for row in cur:
        talent_names[row[1]] = row[0]

    statement = 'SELECT "Most Recent Movie", "Second Recent Movie", "Third Recent Movie" FROM Talent'
    cur.execute(statement)

    movies = []
    for row in cur:
        for movie in row:
            if movie not in movies:
                movies.append(movie)

    movie_instances = []
    for film in movies:
        try:
            results = requests.get("http://www.omdbapi.com", params= {
                'apikey': secrets.OMDB_API_KEY,
                't': film,
            })
            d = json.loads(results.text)
            actors = []
            for actor in d['Actors'].split(','):
                if actor.strip() in talent_names:
                    actors.append(actor.strip())
                elif actor.strip() == 'Robert Downey Jr.':
                    actors.append('Robert Downey, Jr.')

            if len(actors) == 0:
                movie_insertion = (None, d['Title'], d['Year'], d['Rated'],
                                   d['Genre'], None, None, None, None, None, None)
            elif len(actors) == 1:
                movie_insertion = (None, d['Title'], d['Year'], d['Rated'],
                                   d['Genre'], actors[0], talent_names[actors[0]],
                                   None, None, None, None)
            elif len(actors) == 2:
                movie_insertion = (None, d['Title'], d['Year'], d['Rated'],
                                   d['Genre'], actors[0], talent_names[actors[0]],
                                   actors[1], talent_names[actors[1]], None, None)
            elif len(actors) == 3:
                movie_insertion = (None, d['Title'], d['Year'], d['Rated'],
                                   d['Genre'], actors[0], talent_names[actors[0]],
                                   actors[1], talent_names[actors[1]],
                                   actors[2], talent_names[actors[2]])
            statement = "INSERT INTO 'Movies' "
            statement += "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cur.execute(statement, movie_insertion)
        except:
            continue

    conn.commit()
    conn.close()


def graph_one():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Database creation failed")

    statement = 'SELECT Name, "Total Movie Appearances" FROM Talent LIMIT 31'
    cur.execute(statement)
    talent = []
    i = 0
    for row in cur:
        if row[0].split()[0] == 'Jennifer' or row[0].split()[0] == 'Margot' or row[0].split()[0] == 'Scarlett' or row[0].split()[0] == 'Emma' or row[0].split()[0] == 'Gal':
            talent.append(row)
        elif i > 6:
            i += 1
            continue
        else:
            talent.append(row)
        i += 1

    layout = go.Layout(title='Total Movie Appearances From Top 5 Actors and Actresses',
                       xaxis=dict(title='Actors and Actresses'),
                       yaxis=dict(title='Total Movie Appearances'))
    data = [go.Bar(
            x = [name[0] for name in talent],
            y = [name[1] for name in talent]
    )]
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='Total Movies From Top 5 Actors and Actresses')

    conn.commit()
    conn.close()


def graph_two():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Database creation failed")

    state_abbr_dict = {'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AS': 'American Samoa', 'AZ': 'Arizona',
                       'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia', 'DE': 'Delaware',
                       'FL': 'Florida', 'GA': 'Georgia', 'GU': 'Guam', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho',
                       'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana',
                       'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota',
                       'MO': 'Missouri', 'MP': 'Northern Mariana Islands', 'MS': 'Mississippi', 'MT': 'Montana',
                       'NA': 'National', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire',
                       'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio',
                       'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'PR': 'Puerto Rico', 'RI': 'Rhode Island',
                       'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
                       'VA': 'Virginia', 'VI': 'Virgin Islands', 'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin',
                       'WV': 'West Virginia', 'WY': 'Wyoming'}

    statement = 'SELECT Hometown FROM Talent'
    cur.execute(statement)
    homestates = {}
    for row in cur:
        if row[0][-2:] in homestates:
            homestates[row[0][-2:]] += 1
        else:
            homestates[row[0][-2:]] = 1
    new = sorted(homestates, key = lambda x: homestates[x], reverse=True)[:7]
    sorted_homestates = []
    for state in new:
        if state in state_abbr_dict:
            sorted_homestates.append((state_abbr_dict[state], homestates[state]))

    layout = go.Layout(title='5 Most Popular Homestates for Top 50 Actors and Actresses',
                       xaxis=dict(title='Homestate'),
                       yaxis=dict(title='Number of Actors and Actresses Born There'))
    data = [go.Bar(
            x = [state[0] for state in sorted_homestates],
            y = [state[1] for state in sorted_homestates]
    )]

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='5 Most Popular Homestates for Top 50 Actors and Actresses')

    conn.commit()
    conn.close()

def graph_three():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Database creation failed")

    region_abbr_dict = {'Northeast': ['CT', 'ME', 'MA', 'NH', 'RI', 'VT', 'NJ', 'NY', 'PA'],
                        'South': ['DE', 'FL', 'GA', 'MD', 'NC', 'SC', 'VA', 'DC', 'WV', 'AL', 'KY', 'MS', 'TN', 'AR', 'LA', 'OK', 'TX'],
                        'West': ['AZ', 'CO', 'ID', 'MT', 'NV', 'NM', 'UT', 'WY', 'AK', 'CA', 'HI', 'OR', 'WA']}

    regions_dict = {'Northeast USA': 0, 'Southern USA': 0, 'Western USA': 0, 'Canada': 0,
                    'Australia': 0, 'Africa': 0, 'Israel': 0, 'Western Europe': 0}

    statement = 'SELECT Hometown FROM Talent'
    cur.execute(statement)
    for row in cur:
        if row[0][-2:] in region_abbr_dict['Northeast'] or row[0] == 'Washington, D.C.':
            regions_dict['Northeast USA'] += 1
        elif row[0][-2:] in region_abbr_dict['South']:
            regions_dict['Southern USA'] += 1
        elif row[0][-2:] in region_abbr_dict['West'] or row[0] == 'California':
            regions_dict['Western USA'] += 1
        elif row[0].split(', ')[-1] == 'Canada':
            regions_dict['Canada'] += 1
        elif row[0].split(', ')[-1] == 'Australia':
            regions_dict['Australia'] += 1
        elif row[0].split(', ')[-1] == 'Israel':
            regions_dict['Israel'] += 1
        elif row[0].split(', ')[-1] == 'South Africa':
            regions_dict['Africa'] += 1
        elif row[0] == 'Unknown':
            pass
        else:
            regions_dict['Western Europe'] += 1


    labels = list(regions_dict.keys())
    values = list(regions_dict.values())

    layout = go.Layout(title='Top 50 Actors and Actresses Hometowns by Region')
    data = [go.Pie(labels=labels, values=values)]
    fig = go.Figure(data=data, layout=layout)

    py.plot(fig, filename='Top 50 Actors and Actresses Hometowns by Region')

    conn.commit()
    conn.close()

def graph_four():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Database creation failed")

    statement = 'SELECT Name, Hometown FROM Talent'
    cur.execute(statement)

    lat_long_dict = {}
    hometowns = []
    for row in cur:
        if row[1] is not 'Unknown' or 'California':
            baseurl = "https://maps.googleapis.com/maps/api/geocode/json?"
            parameters = {'address': row[1], 'key': secrets.google_places_key}
            result = json.loads(requests.get(baseurl, params = parameters).text)
            latitude = result["results"][0]["geometry"]["location"]["lat"]
            longitude = result["results"][0]["geometry"]["location"]["lng"]
            lat_long_dict[row[0]] = [latitude, longitude]
            hometowns.append(row[1])


    layout = go.Layout(title='World Map of Hometowns of 50 Top Actors and Actresses')
    data = [go.Scattergeo(
            type = 'scattergeo',
            lon = [coordinate[1] for coordinate in list(lat_long_dict.values())],
            lat = [coordinate[0] for coordinate in list(lat_long_dict.values())],
            text = list(lat_long_dict.keys())
    )]

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='World Map of Hometowns of 50 Top Actors and Actresses')

    conn.commit()
    conn.close()

def load_help_text():
    with open('help.txt') as f:
        return f.read()

def interactive_prompt():
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')

        if response == 'help':
            print(help_text)
            continue

        elif response == 'appearances':
            graph_one()
            continue

        elif response == 'homestates':
            graph_two()
            continue

        elif response == 'homeregions':
            graph_three()
            continue

        elif response == 'map':
            graph_four()
            continue

        elif response == 'exit':
            print('GOODBYE!')
            break

        else:
            print("Invalid command. Enter 'exit' to quit the program, or enter 'help' to see a list of valid commands.")

if __name__=="__main__":
    interactive_prompt()
