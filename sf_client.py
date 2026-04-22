from simple_salesforce import Salesforce

from scoring.config import ScoringConfig


def get_salesforce_client(config: ScoringConfig) -> Salesforce:
    return Salesforce(
        username=config.username,
        password=config.password,
        security_token=config.security_token,
        domain=config.domain,
        version=config.api_version,
    )
