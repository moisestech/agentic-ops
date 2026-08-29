from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    agent_host: str = "0.0.0.0"
    agent_port: int = 8080
    agent_provider: str = "fake"
    agent_cors_origins: str = "http://localhost:3000"
    database_url: str = "postgresql://ops:ops@localhost:5433/ops"
    corpus_dir: str = ""
    demo_mode: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.agent_cors_origins.split(",") if item.strip()]


settings = Settings()
