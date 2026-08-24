# Lecture Slides

We use [Marp](https://marp.app) to generate the slides from markdown using the [TUM Marp Template](https://github.com/hofbi/tum-marp-template).

## Setup

Follow the setup on their [website](https://github.com/marp-team/marp-cli) or use our `docker compose.yml` which uses <https://hub.docker.com/r/marpteam/marp-cli>.

## Build

```shell
# Learn the CLI
docker compose run generate --help

# Generate slides
docker compose run generate --input-dir ./<lecture or homework>         # Generate html
docker compose run generate --input-dir ./<lecture or homework> --pdf   # Pdf
docker compose run generate --input-dir ./<lecture or homework> --pptx  # Powerpoint

# Fast Live Serve of lecture slides
docker compose up   # Access the slides on http://localhost:8080
```
