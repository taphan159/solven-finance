import os


class Config:
    """Application configuration for SOLVEN."""

    @property
    def sec_user_agent(self) -> str:
        """
        User-Agent required by SEC EDGAR API.
        Format must be: 'Sample Company Name AdminContact@<sample company domain>.com'
        """
        ua = os.environ.get("SOLVEN_SEC_USER_AGENT")
        if not ua:
            raise ValueError(
                "Environment variable SOLVEN_SEC_USER_AGENT must be set. "
                "Format: 'ProjectName ContactEmail'"
            )
        return ua

    @property
    def sec_api_timeout(self) -> float:
        return float(os.environ.get("SOLVEN_SEC_TIMEOUT", "10.0"))


config = Config()
