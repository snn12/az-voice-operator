# Docker

Container assets for local development and deployment. Nothing is implemented
yet.

Planned:

- `Dockerfile` — multi-stage Python image, non-root user.
- `compose.yaml` — PostgreSQL and the application for local development.
- `.dockerignore` — excludes secrets, audio, datasets, and build output.

No image is buildable at this stage because the application has no entry point.
