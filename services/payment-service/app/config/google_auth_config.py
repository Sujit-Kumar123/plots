from pydantic_settings import BaseSettings


class GoogleAuthConfig(BaseSettings):
    google_client_id: str = ""
    google_client_secret: str = ""
    google_oauth_redirect_uri: str = ""
