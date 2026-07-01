from pydantic_settings import BaseSettings


class AzureAuthConfig(BaseSettings):
    # Azure AD OAuth
    azure_client_id: str = ""
    azure_client_secret: str = ""
    azure_tenant_id: str = "common"
    azure_oauth_redirect_uri: str = ""

    # Azure Blob Storage
    azure_storage_connection_string: str = ""
    azure_storage_container: str = "uploads"
