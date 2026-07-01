# ── Stage 1: Build ────────────────────────────────────────────────────────────
FROM oven/bun:1-alpine AS builder

WORKDIR /app

# Install deps first (cached layer)
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile

# Copy source and build
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1

# Build-time public env vars (injected into the JS bundle at build time)
ARG NEXT_PUBLIC_AUTH_GOOGLE_ENABLED=false
ARG NEXT_PUBLIC_AUTH_AZURE_ENABLED=false
ENV NEXT_PUBLIC_AUTH_GOOGLE_ENABLED=$NEXT_PUBLIC_AUTH_GOOGLE_ENABLED
ENV NEXT_PUBLIC_AUTH_AZURE_ENABLED=$NEXT_PUBLIC_AUTH_AZURE_ENABLED

RUN bun run build

# ── Stage 2: Run ──────────────────────────────────────────────────────────────
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Next.js standalone output includes all required node_modules inline
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs && \
    chown -R nextjs:nodejs /app
USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# BACKEND_INTERNAL_URL: server-side URL the Next.js SSR rewrites use to reach the API Gateway.
# Default works when running alongside the gateway in the same Docker network.
ENV BACKEND_INTERNAL_URL=http://api-gateway:8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', r => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

CMD ["node", "server.js"]
