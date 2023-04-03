from tmdbv3api import TMDb, Movie, Person
from tmdbv3api.exceptions import TMDbException
import requests
import re
import datetime
import textwrap
import popularity as p

# API Key 
import config

# Global Variables
tmdb = TMDb()
database = Movie()
person = Person()
tmdb.api_key = config.api_key
tmdb.language = 'en'
fail_counter = 0
dne_counter = 0
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

    # Handle connection errors or non-existant actors
    while (True):
        try:
            movie = database.details(movie_id)
        except TMDbException:
            dne_counter += 1
            return cast
        except: 
            fail_counter += 1
        else:
            break
    
    movie = database.details(movie_id)
    
    actors = movie.casts['cast']
    for actor in actors:
        cast[actor.id] = actor.name
    return cast

# -----------------------------------------------------------------------   
""" Grab The Movies From A Specific Actor ID """
def get_movies(actor_id):
    # Store movies in dictionary with {movie_id : movie_name}
    movies = {}

    # Handle connection errors or non-existant actors
    while (True):
        try:
            credits = person.movie_credits(actor_id).cast
        except TMDbException:
            dne_counter += 1
            return movies
        except: 
            fail_counter += 1
        else:
            break

    for cred in credits:
        movies[cred.id] = cred.original_title
    return movies

# -----------------------------------------------------------------------   
""" Find All Chains Of A Specified Length (Limit) """
def chainfinder(chain, list, iterations, movie_flag, limit):
    # If the list is a list of movies:
    if (movie_flag):
        # If we reach the limit and the end movie is in the list of movies, we have discovered a valid chain
        if (iterations == limit):
            if (end_movie_id in list):
                new_chain = chain[:]
                new_chain.append((end_movie_id, end_movie))

                # Print the chain and add it to the list of chains
                print("%i. " %(len(chains) + 1), end = "")
                printchain(new_chain)
                chains.append(new_chain)

            return
        # If not at the limit recursively call function for list of cast of each movie
        else:
            for movie in list:
                # Discard the chain if we have come across the movie before, or we have reached the end movie before the limit
                if (any(movie in item for item in chain) or (movie == end_movie_id)):
                    continue
                else:
                    new_chain = chain[:]
                    new_chain.append((movie, list[movie]))
                    cast = get_cast(movie)
                    chainfinder(new_chain, cast, iterations, False, limit)
    # If the list is a list of actors:
    else:
        for actor in list:
            # Discard chain if we have come across the actor before
            if (any(actor in item for item in chain)):
                    continue
            # Recursively call function for list of movies of each actor
            else:
                new_chain = chain[:]
                new_chain.append((actor, list[actor]))
                movies = get_movies(actor)
                chainfinder(new_chain, movies, iterations+1, True, limit)

# -----------------------------------------------------------------------
""" Print Headers And Call Chainfinder Algorithm """
def solutions(id_name, limit):
    # Clear chains and print header
    chains.clear()
    print("\nChains of length %i: " %limit)

    # Find and print all possible chains
    chainfinder([id_name], get_cast(id_name[0]), 0, False, limit)

    # If no chains found print error message, otherwise reprint chains sorted by popularity
    if (not chains):
        print("No chains of length %i connecting the movies was found." %limit)
    else:
        p.popularity(chains)

# -----------------------------------------------------------------------
""" Print Each Chain """
def printchain(chain):
    for step in range(len(chain)-1):
        print("%s -> " % chain[step][1], end = "")
    print(chain[-1][1])

# -----------------------------------------------------------------------
""" Search for Custom Challenge Movies """
def search(start):
     # Loop until user picks a movie
    while (True):
        # Search for the movie
        print("Search for the %s movie: " %("start" if start else "end"))
        search  = database.search(input())

        # Print up to 10 options and prompt user to choose
        for index in range(len(search)):
            if (index >= 10):
                break
            print("\n%i. Name: %s" %(index + 1, search[index].title))
            wrapper=textwrap.TextWrapper(initial_indent = ('   ' if index != 9 else '    '), 
                                         subsequent_indent = (('\t' + '     ') if index != 9 else ('\t' + '      ')), 
                                         width = 120)
            print(wrapper.fill("Overview: " + ("None" if search[index].overview == "" else search[index].overview)))

        # Search yielded no results
        if (len(search) == 0):
            print("\nThe search yielded no options. Press enter to search again.")
            input()
            continue
        # Only one movie option
        if (len(search) == 1):
            print("\nThere is only one option. Press enter to select it or 0 to search again:")
            if (input() == ""):
                return search[0].id, search[0].title
            else:
                print()
        # Multiple options
        else:
            print("\nPick a movie (1-%i) or 0 to search again:" %(len(search) if len(search) <= 10 else 10))
            selection  = int(input()) - 1
            print()
            if (selection != -1): 
                break

    return search[selection].id, search[selection].title
""" Main """

# Initializing chains
chains = [] 

print("\nDo you want to solve the daily challenge, or make your own custom challenge to solve? (D/C)")
daily = input()

# Daily Challenge
if (daily == 'D'):
    challenge = get_daily_challenge()

    start_movie = challenge[0]['title']
    start_movie_id = challenge[0]['id']

    end_movie = challenge[1]['title']
    end_movie_id = challenge[1]['id']

    print("\nDaily Challenge: %s -> %s" %(start_movie, end_movie))

# Custom Challenge
elif (daily == 'C'):
    
    print()
    start_movie_id, start_movie = search(True)
    end_movie_id, end_movie = search(False)
    
    print("\nCustom Challenge: %s -> %s" %(start_movie, end_movie))

# Finding all chains of length 1
solutions((start_movie_id, start_movie), 1)   

# # Finding all chains of length 2
solutions((start_movie_id, start_movie), 2) 

print("\nThere were %i actors or movies that did not exist." %dne_counter)
print("There were %i connection failures." %fail_counter)