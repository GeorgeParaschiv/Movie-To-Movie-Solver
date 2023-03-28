from tmdbv3api import TMDb, Movie, Person
import requests
import re
import datetime
import config

# Global Variables
tmdb = TMDb()
database = Movie()
person = Person()
tmdb.api_key = config.api_key
tmdb.language = 'en'
source_date = "05 Mar 2022 17:00:00"

# Grabbing the Daily Challenge from the Website
url = 'https://movietomovie.com/bundle.js'

response = requests.get(url)

# Extract the movie information from the JavaScript code using regular expressions
regex = r'\[{id:(.*?),title:\"(.*?)\",poster:.*?},{id:(.*?),title:\"(.*?)\",poster:.*?}\]'
matches = re.findall(regex, response.text)

# Create a list of dictionaries containing the different daily challenges
daily_challenges = []

# Parsing the daily challenges into a list
for match in matches:
    start = {'id': int(match[0]), 'title': match[1]}
    end = {'id': int(match[2]), 'title': match[3]}
    daily_challenges.append([start, end])

# Calculating the challenge index based on days since the source date
time = datetime.datetime.strptime(source_date, "%d %b %Y %H:%M:%S")
days_since = (datetime.datetime.now() - time).days
time = days_since % len(daily_challenges)

# Grab the current daily challenge
challenge = daily_challenges[time]

# Initializations
start_movie = challenge[0]['title']
start_movie_id = challenge[0]['id']

end_movie = challenge[1]['title']
end_movie_id = challenge[1]['id']

# Set iteration limit
limit = 1

# Stores the lines with their corresponding popularities [line[]]
lines = []

# -----------------------------------------------------------------------   
# Grab the cast from a specific movie ID
def get_cast(movie_id):
    # Store cast in dictionary with {actor_id : actor_name}
    cast = {}
    movie = database.details(movie_id)
    actors = movie.casts['cast']
    for actor in actors:
        cast[actor['id']] = actor['name']
    return cast

# -----------------------------------------------------------------------   
# Grab the movies from a specific actor ID
def get_movies(actor_id):
    movies = {}
    credits = person.movie_credits(actor_id).cast
    for cred in credits:
        movies[cred.id] = cred.original_title
    return movies

# ----------------------------------------------------------------------- 
def printline(line):
    for step in range(len(line)-1):
        print("%s -> " %line[step], end = "")
    print(line[-1])

# -----------------------------------------------------------------------   
# Recursively search through the movies until end is reach or limit is reach
def linefinder(line, list, iterations, movie_flag):
    if (movie_flag):
        if (iterations == limit):
            if (end_movie_id in list):
                new_line = line[:]
                new_line.append(end_movie)
                printline(new_line)
                lines.append(new_line)
            return
        else:
            for movie in list:
                if (list[movie] in line):
                    continue
                else:
                    new_line = line[:]
                    new_line.append(list[movie])
                    cast = get_cast(movie)
                    linefinder(new_line, cast, iterations, False)
    else:
        for actor in list:
            if (list[actor] in line):
                    continue
            else:
                new_line = line[:]
                new_line.append(list[actor])
                movies = get_movies(actor)
                linefinder(new_line, movies, iterations+1, True)

# -----------------------------------------------------------------------
#            
print("\nDaily Challenge: %s -> %s" %(start_movie, end_movie))

# Finding all lines of length 1
print("\nLines of length 1: ")
linefinder([start_movie], get_cast(start_movie_id), 0, False)

if (not lines):
    print("No lines of length %i connecting the movies was found.\n" %limit)

limit+=1    

# Finding all lines of length 2
print("\nLines of length 2: ")
linefinder([start_movie], get_cast(start_movie_id), 0, False)

if (not lines):
    print("No lines of length %i connecting the movies was found." %limit)

