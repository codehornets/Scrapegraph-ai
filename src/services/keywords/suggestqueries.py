import requests
import json
import pandas as pd

# =============================================================================
# Keyword Suggestor for Keyword Research
# =============================================================================

# keyword = input("Add your keyword: ")

services = {
    "amazon": "//completion.amazon.co.uk/search/complete?method=completion&search-alias=aps&mkt=3&callback=?&q=",
    "baidu": "//suggestion.baidu.com/su?cb=?&wd=",
    "bing": "//api.bing.com/osjson.aspx?JsonType=callback&JsonCallback=?&query=",
    "ebay": "//autosug.ebay.com/autosug?_jgr=1&sId=0&_ch=0&callback=?&kwd=",
    "google": "//suggestqueries.google.com/complete/search?client=chrome&q=",
    "google_firefox": "http://suggestqueries.google.com/complete/search?output=firefox&q=",
    "google_news": "//suggestqueries.google.com/complete/search?client=chrome&hl=${lang}&ds=n&gl=${country}&callback=?&q=",
    "google_shopping": "//suggestqueries.google.com/complete/search?client=chrome&hl=${lang}&ds=sh&gl=${country}&callback=?&q=",
    "google_books": "//suggestqueries.google.com/complete/search?client=chrome&hl=${lang}&ds=bo&gl=${country}&callback=?&q=",
    "google_play": "//market.android.com/suggest/SuggRequest?json=1&c=0&hl=${lang}&gl=${country}&callback=?&query=",
    "google_play_apps": "//market.android.com/suggest/SuggRequest?json=1&c=3&hl=${lang}&gl=${country}&callback=?&query=",
    "google_play_movies": "//market.android.com/suggest/SuggRequest?json=1&c=4&hl=${lang}&gl=${country}&callback=?&query=",
    "google_play_books": "//market.android.com/suggest/SuggRequest?json=1&c=1&hl=${lang}&gl=${country}&callback=?&query=",
    "google_videos": "//suggestqueries.google.com/complete/search?client=chrome&hl=${lang}&ds=v&gl=${country}&callback=?&q=",
    "google_images": "//suggestqueries.google.com/complete/search?client=chrome&hl=${lang}&ds=i&gl=${country}&callback=?&q=",
    "twitter": "//twitter.com/i/search/typeahead.json?count=30&result_type=topics&src=SEARCH_BOX&callback=?&q=",
    "yahoo": "//search.yahoo.com/sugg/ff?output=jsonp&appid=ffd&callback=?&command=",
    "yandex": "//yandex.com/suggest/suggest-ya.cgi?callback=?&q=?&n=30&v=4&uil={lang}&part=",
    "youtube": "//suggestqueries.google.com/complete/search?client=chrome&hl=${lang}&ds=yt&gl=${country}&callback=?&q=",
}

# =============================================================================
# Add try except on suggestions = json.loads.. in the case the api doesnt reutrn anything, the code should keep going
# =============================================================================


"""
api_call makes the first api call to get the initial 10 queries
We only need one parameter which is the initial Keyword we want 
to get ideas from. We create a list called Keywords that we store
all the keywords

End of function we call 3 other functions to build up the keywords list
"""


def suggest_queries_for_keyword(keyword):

    keywords = [keyword]

    url = services["google_firefox"] + keyword
    response = requests.get(url, verify=False)
    suggestions = json.loads(response.text)

    for word in suggestions[1]:
        keywords.append(word)

    # functions for getting more kws, cleaning and search volume
    prefixes(keyword, keywords)
    suffixes(keyword, keywords)
    numbers(keyword, keywords)
    get_more(keyword, keywords)
    clean_df(keywords, keyword)


"""
prefixes adds a value from the prefix list before the keyword we passed 
and get suggestions out of that. Then it appends each of the keyword to 
the keywords lists.

function passes to parameters:
    keyword: value we want to check.
    keywords: list to append values.
"""


def prefixes(keyword, keywords):
    # we can add more suffixes tailored to the company or type of search we are looking. E.g: food delivery, delivery,etc
    prefixes = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "y",
        "x",
        "y",
        "z",
        "how",
        "which",
        "why",
        "where",
        "who",
        "when",
        "are",
        "what",
    ]

    for prefix in prefixes:
        print(prefix)
        url = services["google_firefox"] + prefix + " " + keyword
        response = requests.get(url, verify=False)
        suggestions = json.loads(response.text)

        kws = suggestions[1]
        length = len(kws)

        for n in range(length):
            print(kws[n])
            keywords.append(kws[n])


"""
suffixes adds a value from the prefix list after the keyword we passed 
and get suggestions out of that. Then it appends each of the keyword to 
the keywords lists.

function passes to parameters:
    keyword: value we want to check.
    keywords: list to append values.
"""


def suffixes(keyword, keywords):
    # we can add more suffixes tailored to the company or type of search we are looking. E.g: food delivery, delivery,etc
    suffixes = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "y",
        "x",
        "y",
        "z",
        "like",
        "for",
        "without",
        "with",
        "versus",
        "vs",
        "to",
        "near",
        "except",
        "has",
    ]

    for suffix in suffixes:
        print(suffix)
        url = services["google_firefox"] + keyword + " " + suffix
        response = requests.get(url, verify=False)
        suggestions = json.loads(response.text)

        kws = suggestions[1]
        length = len(kws)

        for n in range(length):
            print(kws[n])
            keywords.append(kws[n])


"""
Numbers runs a for loop from 0 to 9 and appends the number as a string
at the end of the keyword. E.g Broncos 2.  this can give something like 
Broncos 2020 or Broncos 2021 team


function passes to parameters:
    keyword: value we want to check.
    keywords: list to append values.
"""


def numbers(keyword, keywords):
    # we can add more numbers
    for num in range(0, 10):
        print(num)
        url = services["google_firefox"] + keyword + " " + str(num)
        response = requests.get(url, verify=False)
        suggestions = json.loads(response.text)

        kws = suggestions[1]
        length = len(kws)

        for n in range(length):
            print(kws[n])
            keywords.append(kws[n])


"""
get more takes the keywords list and runs the keywords via the
api to get more suggestions. Every new suggestion is stored back in
the keywords list.

I set a limit of 1000 Keywords but this can be increased.
Once it hits 1000 keyowords it stops
"""


def get_more(keyword, keywords):
    for i in keywords:
        print(i)
        url = services["google_firefox"] + i
        response = requests.get(url, verify=False)
        suggestions = json.loads(response.text)

        keywords2 = suggestions[1]
        length = len(keywords2)

        for n in range(length):
            print(keywords2[n])
            keywords.append(keywords2[n])
            print(len(keywords))

        if (
            len(keywords) >= 1000
        ):  # we can increase this number if we want more keywords
            print("###Finish here####")
            break


"""
cleand df performs 2 important things:
    - Remove dupliactes fro the list
    - Remove keywords that dont contain the primary keyword.
    
e.g: if we searched for Netlfix and playstation is on the list. 
    palaystation will be removed.
    
"""


def clean_df(keywords, keyword):
    # removing duplicates from the list
    keywords = list(dict.fromkeys(keywords))

    # checking if keyword is in the list and removing anything that doesnt contain th keyword
    new_list = [
        word for word in keywords if all(val in word for val in keyword.split(" "))
    ]

    # tranforming list into dataframe for excell extraction
    df = pd.DataFrame(new_list, columns=["Keywords"])

    # We can comment this
    print(df)

    # Exporting all keywords to CSV
    df.to_csv(keyword + "-keywords.csv")

    # this is just in case we want to create an API response
    json_hist = df.to_json(orient="columns")

    return json_hist


# api_call(keyword)
