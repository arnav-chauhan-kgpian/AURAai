"""Production entrypoint: ``python -m app``.

Reads the listen port from ``$PORT`` (injected by platforms like Railway) inside
Python, so the start command needs no shell variable expansion — it is just
``python -m app``. This sidesteps exec-form start commands where ``$PORT`` would
otherwise reach uvicorn as a literal string.
"""

import os

import uvicorn


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        # Trust the platform proxy's X-Forwarded-* headers (HTTPS termination).
        proxy_headers=True,
        forwarded_allow_ips="*",
        # Drain in-flight requests on SIGTERM.
        timeout_graceful_shutdown=30,
    )


if __name__ == "__main__":
    main()
