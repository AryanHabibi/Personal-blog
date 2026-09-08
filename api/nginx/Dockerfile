# syntax=docker/dockerfile:1

# Production nginx: the reverse-proxy config is baked into the image so the
# container ships self-contained (no host bind mounts). Build context is
# api/nginx/, so the COPY sources are the files sitting next to this file.
FROM nginx:1.27-alpine

# Drop the stock welcome vhost; ours replaces it.
RUN rm -f /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# Note: no `nginx -t` here - it resolves the `api` upstream hostname, which
# doesn't exist during the build. The config is validated at container start.

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/nginx-health || exit 1
