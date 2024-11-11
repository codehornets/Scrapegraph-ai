import json
import logging
import time
from urllib.parse import urljoin

import jwt
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from libs.spellchecker.src.config.settings import Settings


class RequestService:
    def __init__(self, settings: Settings):
        self.settings, self.CONTENT_TYPE = settings, "application/json"

    @staticmethod
    def _validate_token(token):
        return (
            time.time() < jwt.decode(token, options={"verify_signature": False})["exp"]
        )

    def _fetch_token(self):
        token = (
            OAuth2Session(
                client=BackendApplicationClient(
                    client_id=self.settings.quickauth_client_id
                )
            ).fetch_token(
                token_url=urljoin(self.settings.quickauth_uri, "/oauth/token"),
                client_id=self.settings.quickauth_client_id,
                client_secret=self.settings.quickauth_client_secret,
            )
            if self.settings.quickauth_uri
            else None
        )
        return (
            (token["access_token"], token["expires_in"])
            if token and self._validate_token(token["access_token"])
            else (None, None)
        )

    def make_authenticated_request(
        self, url, method="GET", data=None
    ) -> requests.Response:
        token, expiration = self._fetch_token()
        if token is None:
            raise EnvironmentError("Could not fetch token from Quick Auth")
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": self.CONTENT_TYPE,
            "Content-Type": self.CONTENT_TYPE,
            "Access-Control-Allow-Origin": "*",
        }
        response = requests.request(
            method,
            url,
            headers=headers,
            data=json.dumps(data or [], ensure_ascii=False).encode("utf-8"),
            verify=self.settings.app_env.upper() != "LOCAL",
        )
        if response.status_code != 200:
            logging.error(
                f"Failed to send spelling errors to MLR API. Status code: {response.status_code}"
            )
        return response
