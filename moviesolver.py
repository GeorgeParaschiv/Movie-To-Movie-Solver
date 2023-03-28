from tmdbv3api import TMDb, Movie, Person, Authentication
import requests
import re
import datetime

# API Key 
import config

# Global Variables
tmdb = TMDb()
database = Movie()
person = Person()
tmdb.api_key = config.api_key
tmdb.language = 'en'

# -----------------------------------------------------------------------
""" Get The Daily Challenge """
def get_daily_challenge():
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
    time = datetime.datetime.strptime("05 Mar 2022 13:00:00", "%d %b %Y %H:%M:%S")
    days_since = (datetime.datetime.now() - time).days
    time = days_since % len(daily_challenges)

    # Grab the current daily challenge
    return daily_challenges[time]

# -----------------------------------------------------------------------
""" Grab The Cast From A Specific Movie ID """
def get_cast(movie_id):
    # Store cast in dictionary with {actor_id : actor_name}
    cast = {}
    movie = database.details(movie_id)
    actors = movie.casts['cast']
    for actor in actors:
        cast[actor['id']] = actor['name']
    return cast

# -----------------------------------------------------------------------   
""" Grab The Movies From A Specific Actor ID """
def get_movies(actor_id):
    movies = {}
    credits = person.movie_credits(actor_id).cast
    for cred in credits:
        movies[cred.id] = cred.original_title
    return movies

# -----------------------------------------------------------------------
""" Print Each Chain """
def printchain(chain):
    for step in range(len(chain)-1):
        print("%s -> " %chain[step], end = "")
    print(chain[-1])

# -----------------------------------------------------------------------   
""" Find All Chains Of A Specified Length (Limit) """
def chainfinder(chain, list, iterations, movie_flag, limit):
    # If the list is a list of movies:
    if (movie_flag):
        # If we reach the limit and the end movie is in the list of movies, we have discovered a valid chain
        if (iterations == limit):
            if (end_movie_id in list):
                new_chain = chain[:]
                new_chain.append(end_movie)
                # Print the chain and add it to the list of chains
                printchain(new_chain)
                chains.append(new_chain)
                # Refresh authentication to avoid crashing
                auth = Authentication(username=config.username, password=config.password) 
            return
        # If not at the limit recursively call function for list of cast of each movie
        else:
            for movie in list:
                # Discard the chain if we have come across the movie before, or we have reached the end movie before the limit
                if ((list[movie] in chain) or (movie == end_movie_id)):
                    continue
                else:
                    new_chain = chain[:]
                    new_chain.append(list[movie])
                    cast = get_cast(movie)
                    chainfinder(new_chain, cast, iterations, False, limit)
    # If the list is a list of actors:
    else:
        for actor in list:
            # Discard chain if we have come across the chain before
            if (list[actor] in chain):
                    continue
            # Recursively call function for list of movies of each actor
            else:
                new_chain = chain[:]
                new_chain.append(list[actor])
                movies = get_movies(actor)
                chainfinder(new_chain, movies, iterations+1, True, limit)

# -----------------------------------------------------------------------
""" Print Headers And Call Chainfinder Algorithm """
def solutions(title, id, limit):
    print("\nChains of length %i: " %limit)
    chainfinder([title], get_cast(id), 0, False, limit)

    if (not chains):
        print("No chains of length %i connecting the movies was found." %limit)

# -----------------------------------------------------------------------
""" Main """

# Initializations
challenge = get_daily_challenge()
chains = [] 

# start_movie = challenge[0]['title']
# start_movie_id = challenge[0]['id']

# end_movie = challenge[1]['title']
# end_movie_id = challenge[1]['id']

start_movie = "(500) Days of Summer"
start_movie_id = 19913

end_movie = "The Wolf of Wall Street"
end_movie_id = 106646

# Daily Challenge Solutions
print("\nDaily Challenge: %s -> %s" %(start_movie, end_movie))

# Finding all chains of length 1
solutions(start_movie, start_movie_id, 1)   

# Finding all chains of length 2
solutions(start_movie, start_movie_id, 2)   