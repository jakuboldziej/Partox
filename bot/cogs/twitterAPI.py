import discord
from discord.ext import commands, tasks

import requests
import json
import tweepy
from dotenv import load_dotenv
import os

class TwitterAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv("API_SECRET")
        self.access_token = os.getenv("ACCESS_TOKEN")
        self.access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
        self.bearer_token = os.getenv("BEARER_TOKEN")
        load_dotenv()

    def auth(self):
        auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)

        return tweepy.API(auth)
    
    def bearer_oauth(self, r):
      r.headers["Authorization"] = f"Bearer {self.bearer_token}"
      r.headers["User-Agent"] = "v2UserTweetsPython"
      
      return r
    
    def connect_to_endpoint(self, url, params):
      response = requests.request("GET", url, auth=self.bearer_oauth, params=params)
      print(response.status_code)
      if response.status_code != 200:
          raise Exception(
              "Request returned an error: {} {}".format(
                  response.status_code, response.text
              )
          )
      return response.json()
    
    @commands.command()
    async def get_tweets(self, ctx):
        url = "https://api.twitter.com/2/users/relffum0/tweets"
        params = {"tweet.fields": "created_at"}
        json_response = self.connect_to_endpoint(url, params)
        print(json_response)

        await ctx.send(json.dumps(json_response, indent=4, sort_keys=True))

async def setup(bot):
    await bot.add_cog(TwitterAPI(bot))