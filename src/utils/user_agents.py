import logging
import os
import random
import requests
from bs4 import BeautifulSoup
from functools import cached_property
from time import time
from typing import List

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

USER_AGENT_URL = "https://www.useragentlist.net/"


def get_user_agents() -> List[str]:
    """Fetch and parse user agents from the user agent list website."""
    try:
        request = requests.get(USER_AGENT_URL)
        request.raise_for_status()
        soup = BeautifulSoup(request.text, "html.parser")
        return [
            user_agent.text.strip() for user_agent in soup.select("pre.wp-block-code")
        ]
    except requests.RequestException as e:
        logger.error(f"Error fetching user agents: {e}")
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
        ]


class UserAgent:
    """Container for a User-Agent"""

    def __init__(self, string: str) -> None:
        self.string = string
        try:
            from user_agents import parse

            self.parsed_string = parse(self.string)
        except ImportError:
            logger.warning(
                "Failed to import 'parse' from user_agents. Make sure the library is installed."
            )
            self.parsed_string = None
        except Exception as e:
            logger.warning(f"Failed to parse User-Agent string. Error: {str(e)}")
            self.parsed_string = None
        self.last_used = int(time())

    @cached_property
    def browser(self) -> str:
        return self.parsed_string.browser.family if self.parsed_string else "Unknown"

    @cached_property
    def browser_version(self) -> float:
        try:
            return (
                float(self.parsed_string.browser.version_string)
                if self.parsed_string
                else 0.0
            )
        except ValueError:
            return 0.0

    @cached_property
    def os(self) -> str:
        return self.parsed_string.os.family if self.parsed_string else "Unknown"

    @cached_property
    def os_version(self) -> str:
        if self.parsed_string:
            return f"{self.parsed_string.os.version_string}"
        return "Unknown"

    def __str__(self) -> str:
        return self.string


class UserAgentRotator:
    """Weighted random User-Agent rotator"""

    def __init__(self, user_agents: List[str]):
        self.user_agents = [UserAgent(ua) for ua in user_agents]

    def weigh_user_agent(self, user_agent: UserAgent):
        """Assign weights to User-Agents based on usage, browser, and OS."""
        weight = 1000 + (time() - user_agent.last_used)
        if user_agent.browser == "Chrome":
            weight += 100
        if user_agent.browser_version:
            weight += user_agent.browser_version * 10
        if user_agent.os == "Mac OS X":
            weight += 100
        elif user_agent.os == "Windows":
            weight += 150
        elif user_agent.os == "Android":
            weight -= 100
        return weight

    def get(self) -> UserAgent:
        """Select a User-Agent based on the assigned weights."""
        user_agent_weights = [self.weigh_user_agent(ua) for ua in self.user_agents]
        selected_user_agent = random.choices(
            self.user_agents, weights=user_agent_weights, k=1
        )[0]
        selected_user_agent.last_used = time()
        return selected_user_agent


def get_random_proxy(proxies: List[str] = None) -> str:
    if proxies := proxies or os.getenv("PROXIES", "").split(","):
        return random.choice(proxies)
    else:
        raise ValueError(
            "No proxies available. Ensure proxies are defined in the environment."
        )
