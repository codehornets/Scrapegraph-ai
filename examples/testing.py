import json
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
graph_config = {
   "llm": {
      "api_key": openai_key,
      "model": "openai/gpt-3.5-turbo",
   },
}

# ************************************************
# Create the SmartScraperGraph instance and run it
# ************************************************

smart_scraper_graph = SmartScraperGraph(
   prompt="List me all the projects with their description.",
   # also accepts a string with the already downloaded HTML code
   source="https://codehornets.com/projects/",
   config=graph_config
)

result = smart_scraper_graph.run()
print(json.dumps(result, indent=2))