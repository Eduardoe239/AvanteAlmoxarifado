# --- Etapa de build ---
FROM node:22-slim AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
# NEXT_PUBLIC_API_URL precisa existir no momento do build, pois o Next.js
# embute variáveis NEXT_PUBLIC_* no bundle do cliente em tempo de build.
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
RUN npm run build

# --- Etapa final (imagem enxuta, sem ferramentas de build) ---
FROM node:22-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "run", "start"]
