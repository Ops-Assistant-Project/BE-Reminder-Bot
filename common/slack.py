class SlackBotName:
    REMINDER_BOT = "REMINDER_BOT"

class SlackEnvKey:
    """
    Slack Bot 환경변수 키 정의

    ⚠️ 주의
    - 현재는 개발 / 포트폴리오용 값
    - 토큰 값은 반드시 crypto 암호화 후 저장할 것
    """

    BOT_TOKENS = {
        SlackBotName.REMINDER_BOT: "gAAAAABpbJONee7hMTjy6rA0vImp9rY8i64WWj4wcH0PuCfaXI5cf3CQfFSM1ooZuR41T8jWFN_jyq1KbOl8mWoks0h-NoW4jufJjbreTqlJpVwTgRApmTNEV8f3mW5V3DBHlYChQjw2K-SSPuPBv9OegZIQtyIPzg==",
    }

    SIGNING_SECRETS = {
        SlackBotName.REMINDER_BOT: "gAAAAABpbJMJkKj6O6uIp84ZP8TMzRZ2E73POK_DUzXz8BTZRIwFJUkcylo_B8VZ-laDimRY777OdQtOhFpbuphT7E49UCMXVQfLFc95n7P0vQLTtUJ1oJOIJK9kKaaBNXPQEr0DNFbQ",
    }
