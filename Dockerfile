# ──────────────────────────────────────────────
# Stage 1: Builder | install dependencies
# ──────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS builder

ENV UV_LINK_MODE=copy

WORKDIR /app

# Install production deps without the project itself (layer-cached)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy source and install the project
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

FROM builder AS builder-dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ──────────────────────────────────────────────
# Stage 2: Runtime | lean base for all targets
# ──────────────────────────────────────────────
FROM python:3.14-slim AS runtime

COPY --chmod=755 entrypoint.sh /usr/local/bin/entrypoint.sh

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app
ENTRYPOINT ["entrypoint.sh"]

# ──────────────────────────────────────────────
# Targets
# ──────────────────────────────────────────────
FROM runtime AS prod
CMD ["prod"]

FROM runtime AS dev
COPY --from=builder-dev /app/.venv /app/.venv
CMD ["dev"]
