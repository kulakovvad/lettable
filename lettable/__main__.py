import argparse
import asyncio
import os
from .agent import create_agent
from .runtime import Runtime
from .store import Store
from .config import load_config


def main():
    parser = argparse.ArgumentParser(description="Local Lettable agent prototype")
    parser.add_argument("message")
    parser.add_argument("--conversation", default="local-demo")
    parser.add_argument("--request-id", required=True)
    args = parser.parse_args()
    load_config()
    if not os.environ.get("OPENAI_API_KEY"):
        parser.error("Set OPENAI_API_KEY in your environment; never paste it into chat")
    runtime = Runtime(create_agent(), Store("lettable.sqlite"))
    outcome = asyncio.run(runtime.start(principal="local-developer", conversation=args.conversation,
                                        request_id=args.request_id, message=args.message))
    print(outcome.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
