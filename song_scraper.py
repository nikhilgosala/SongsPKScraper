"""song_scraper.py: Downloads all the songs of movies starting with a given alphabet."""

__author__      = "Nikhil Bharadwaj"
__license__     = "MIT License"
__version__     = "Python 3.5"

import sys, os, requests, warnings
from bs4 import BeautifulSoup
import urllib.request

error_count_alphabet = 0         #Keeps a track of number of errors in getting all the movies of a given alphabet
error_count = 0                 #Keeps a track of number of errors for a given movie
error_count_download = 0        #Keeps a track of number of errors for a given song
DOWNLOADPATH = os.path.expanduser('~/Desktop/SongsPK')           #Default download path

############################################################## FUNCTION TO GET ALL SONGS FROM A WEBPAGE ##################################################

def downloadMovieSongs(movie_url):
    """Download songs from URL of movie"""
    global error_count
    global error_count_download
    if(movie_url.startswith('www')):
        movie_url = movie_url.replace("http://www")
    try:
        moviepage_data = requests.get(movie_url).content    #Get the HTML content of the movie
        song_url_list = get_songs_names(moviepage_data)
        song_count = 0
        for song_url in list(set(song_url_list)):
            error_count_download = 0            #Reset the error download coiunt for each song
            song_count = song_count + 1
        
            res, resolved_url = url_resolver(song_url)           #Resolve the url pointed to by the Song URL

            if(resolved_url.endswith(".mp3") and not resolved_url.startswith("..")):     #Check if the URL pointed to is a song 
                save_mp3(res, resolved_url.split('/')[-1])
                error_count = 0
    except:
        if error_count >= 10:           #This is the recursion break condition
            print("Error count exceeded. Adding to Movie Alert")
            movie_alert(movie_url)
            error_count = 0
            return
        
        while(error_count < 10):
            print("(downloadMovieSongs) Error connecting to server...Retrying\n")
            error_count += 1
            downloadMovieSongs(movie_url)       #Retry for 10 times

############################################################## FUNCTION TO DOWNLOAD THE MP3 SONG ONTO THE COMPUTER ##################################################        
        
def save_mp3(link, filename):
    """Save mp3 file with given filename"""
    global error_count_download
    print(filename)
    name = (link.geturl()).split('/')
    folder_name = os.path.expanduser(DOWNLOADPATH + '/' + name[-2] + '/')       #The folder where the songs must be downloaded
    if not os.path.exists(folder_name):         #If folder does not exist
        os.mkdir(folder_name)                   #Make a new folder

    fullpath = folder_name + filename
    print(fullpath)

    try:
        if not os.path.exists(fullpath):                #Check if file exists. If yes, then continue...Else download file
            with open(fullpath, 'wb') as output:
                while True:
                    buffer = link.read(65536)           #Read 65536 bytes in one go and repeat until the whole file is downloaded
                    if not buffer:
                        break
                    output.write(buffer)
            error_count_download = 0                    #Reset error count
        else:
            print("Already downloaded...Skipping the song")

    except:
        if error_count_download >= 10:
            print("Error count exceeded. Adding to Song Alert")
            song_alert(filename)
            error_count_download = 0
            return
        
        os.remove(fullpath)                             #Delete any incomplete files
        while(error_count_download < 10):
            print("(save_mp3) Error connecting to server...Retrying\n")
            error_count_download += 1
            save_mp3(link, filename)

############################################################## FUNCTION TO FIND WHERE THE URL LEADS TO ########################################################
        
def url_resolver(url):
    """Find the path of redirection of the URL"""
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    res = opener.open(urllib.request.Request(url))  # Resolve the redirects and gets the song
    return res, res.geturl()

############################################################## FUNCTION TO GET ALL MOVIE NAMES FROM A WEBPAGE ##################################################

def get_movie_names(url_data):
    """Get all the movies from the webpage"""
    soup = BeautifulSoup(url_data, 'html.parser')
    data = soup.findAll('ul', attrs={'class' : 'ctlg-holder'})      #Get all the lines from HTML that are a part of ul with class = 'ctlg-holder'

    movie_list = []
    for div in data:
        links = div.findAll('a')    #Choose all the lines with links
        for a in links:
            if a is not None and a is not "#":
                movie_list.append(a.get('href', None))

    print("Movie Names Obtained")
    return movie_list

############################################################## FUNCTION TO GET ALL THE SONG NAMES FROM A WEBPAGE ##################################################

def get_songs_names(moviepage_data):
    """Get all the songs from the webpage"""
    soup = BeautifulSoup(moviepage_data, 'html.parser')
    data = soup.findAll('a')   #Choose all lines with links
    
    song_list = []
    for a in data:
        url = a.get('href', None)
        if url and "songid=" in url:    #All URLs that point to an mp3 file have songid attribute in them
            song_list.append(url)

    print("Song Names Obtained")
    return song_list

############################################################## FUNCTION TO ALERT USER ABOUT MOVIE DOWNLOAD ERROR ##################################################

def movie_alert(movie_name):
    filename = DOWNLOADPATH + '/' + 'movie_alert.txt'

    movie_alert_file = open(filename, 'a+')

    movie_alert_file.write(movie_name)
    movie_alert_file.write("\n\r")

    movie_alert_file.close();
    
############################################################## FUNCTION TO ALERT USER ABOUT SONG DOWNLOAD ERROR ##################################################

def song_alert(song_name):
    filename = DOWNLOADPATH + '/' + 'song_alert.txt'

    song_alert_file = open(filename, 'a+')

    song_alert_file.write(song_name)
    song_alert_file.write("\n\r")

    song_alert_file.close();

############################################################## FUNCTION TO GET ALL THE MOVIES OF THE GIVEN ALPHABET ##################################################
        
def downloadAlphabetSongs(first_alphabet):
    """Geat all the movies of a given alphabet"""
    global error_count
    global error_count_alphabet
    
    try:
        url = "http://www.songspk.link/%s_list.html" % first_alphabet
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
        url_html = requests.get(url, timeout=100, headers = headers).content     #Gets the HTML code of webpage pointed to by url
        print("Source Code Obtained")
        
        alphabet_movie_list = {}    #Stores the MovieID (Generated Locally) and Name 
        count = 0       #Keeps a count of number of movies starting with given alphabet

        for movie_url in get_movie_names(url_html):
            if not movie_url.startswith('..'):
                alphabet_movie_list[str(count)] = movie_url
                count = count + 1

        movie_url = ""      #Stores the Movie URL
        for movie_id in alphabet_movie_list:
            error_count = 0             #Reset error count for each movie
            
            if not alphabet_movie_list[movie_id].startswith('http://'):         #Some movies have the complete URL. Omitting those
                if not alphabet_movie_list[movie_id] == '#':                    #Some movies have no URL. They have only #. Omitting those
                    movie_url = "http://songspk.link/%s" % alphabet_movie_list[movie_id]
            downloadMovieSongs(movie_url)

    except:
        if(error_count_alphabet >= 10):         #End program if it could not download the movie list in 10 tries
            print("Error count exceeded. Please check your internet connection\n")
            return       

        while(error_count_alphabet < 10):
            error_count_alphabet += 1
            print("Error fetching the movies of the given alphabet...Retrying\n")
            downloadAlphabetSongs(first_alphabet)

##############################################################    MAIN   ############################################################################

first_alphabet = input("Enter the first alphabet of the movies whose songs you want to download [a-z] or 'numeric'\n")
error_count = 0
error_count_download = 0
error_count_alphabet = 0
if not os.path.exists(DOWNLOADPATH):
    os.mkdir(DOWNLOADPATH)
downloadAlphabetSongs(first_alphabet);
    
    
