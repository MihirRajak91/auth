"""Application entrypoint for running the auth API."""

from __future__ import annotations

from auth import create_app

app = create_app()


def main() -> None:
    """Run the development server."""
    app.run(debug=True)


if __name__ == "__main__":
    main()
