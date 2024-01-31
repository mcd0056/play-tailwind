import json
import os
import yfinance as yf
import requests
# from pycoingecko import CoinGeckoAPI
import requests
import os



def get_stock_price(symbol: str) -> float:
    stock = yf.Ticker(symbol)
    price = stock.history(period="1d")['Close'].iloc[-1]
    return price

def get_weather(location: str) -> str:
    url = f"https://wttr.in/{location}?format=3"
    response = requests.get(url)
    return response.text.strip()

# # New Function: Get Crypto Price
# def get_crypto_price(crypto_id: str, currency: str = 'usd') -> float:
#     cg = CoinGeckoAPI()
#     try:
#         price = cg.get_price(ids=crypto_id, vs_currencies=currency)
#         return price[crypto_id][currency]
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None



def find_recipe(ingredients: list) -> list:
    """
    Find recipes based on the provided ingredients using Edamam API.

    :param ingredients: A list of ingredients to include in the recipe search.
    :return: A list of recipes that include the specified ingredients.
    """
    app_id = os.environ["APP_ID"]  # Replace with your actual Edamam App ID
    app_key = os.environ["APP_KEY"]  
    base_url = "https://api.edamam.com/api/recipes/v2"

    try:
        # Convert the list of ingredients into a comma-separated string
        ingredients_str = ",".join(ingredients)

        # Set up the query parameters
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "type": "public",
            "q": ingredients_str
        }

        # Make the API request
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad requests

        # Parse and return the response
        recipes = response.json()
        return recipes

    except requests.RequestException as e:
        return {"error": str(e)}

def get_exchange_rate(base_currency: str) -> dict:
  """
  Retrieve exchange rates for a given base currency using the ExchangeRate-API.

  :param base_currency: The base currency code (ISO 4217 format).
  :return: A dictionary containing exchange rates.
  """
  api_key = os.environ["EXCHANGE_RATE_API_KEY"] # Replace with your actual ExchangeRate-API key
  base_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"

  try:
      # Make the API request
      response = requests.get(base_url)
      response.raise_for_status()  # Raises an HTTPError for bad requests

      # Parse and return the response
      rates = response.json()
      return rates

  except requests.RequestException as e:
      return {"error": str(e)}


def duckduckgo_search(query: str) -> str:
  """
  Perform a web search using DuckDuckGo's Instant Answer API and return the results.

  :param query: The search query.
  :return: A string containing the search results in JSON format.
  """
  url = "https://api.duckduckgo.com/"
  params = {
      "q": query,
      "format": "json"
  }

  try:
      response = requests.get(url, params=params)
      response.raise_for_status()
      return response.text  # Return the response text directly
  except requests.exceptions.RequestException as e:
      print(f"Request Error: {e}")
      return json.dumps({"error": str(e)})


def fetch_news(query):
  api_key = os.environ["NEWS_API_KEY"] # Replace with your actual News API key
  url = f"https://newsdata.io/api/1/news?apikey={api_key}&q={query}&language=en"



  payload = {}
  headers = {}

  response = requests.request("GET", url, headers=headers, data=payload)
  news_data = json.loads(response.text)

  if 'results' in news_data:
      news_list = []
      for article in news_data['results']:
          news_info = {
              "title": article.get('title', 'No title available'),
              "description": article.get('description', 'No description available'),
              "link": article.get('link', 'No link available'),
              "published_date": article.get('pubDate', 'No date available')
          }
          news_list.append(news_info)
      return news_list
  else:
      return "No news found for your query."



