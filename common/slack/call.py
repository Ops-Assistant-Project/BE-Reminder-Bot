import logging
from slack_sdk.errors import SlackApiError


logger = logging.getLogger(__name__)

def slack_call(func, *, action: str, **kwargs):
    try:
        return func(**kwargs)

    except SlackApiError as e:
        error_code = e.response.get("error")
        logger.exception(
            "[SlackApiError]",
            extra={
                "action": action,
                "error": error_code,
                "params": kwargs,
            }
        )
        raise

    except Exception:
        logger.exception(
            "[UnexpectedSlackError]",
            extra={
                "action": action,
                "params": kwargs,
            }
        )
        raise

def slack_call_safe(func, *, action: str, **kwargs):
    try:
        return slack_call(func, action=action, **kwargs)
    except Exception:
        return None
