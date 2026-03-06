from agent.config import settings


def main() -> None:
    print("Local LLM Security Agent PoC")
    print(f"OLLAMA_MODEL={settings.ollama_model}")
    print(f"OLLAMA_HOST={settings.ollama_host}")
    print(f"LOG_LEVEL={settings.log_level}")


if __name__ == "__main__":
    main()
