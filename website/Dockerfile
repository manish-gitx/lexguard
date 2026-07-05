FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_LEXGUARD_API_URL=https://lexguard-api-3mvnlmbu5q-el.a.run.app
ARG NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyCiQjE72J2zXzPtPuTld9jBCudD9EZ0AvM
ARG NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=lexguard-manish-75853.firebaseapp.com
ARG NEXT_PUBLIC_FIREBASE_PROJECT_ID=lexguard-manish-75853
ARG NEXT_PUBLIC_FIREBASE_APP_ID=1:311207483497:web:9db59beecf7c86df282af8
ENV NEXT_PUBLIC_LEXGUARD_API_URL=${NEXT_PUBLIC_LEXGUARD_API_URL}
ENV NEXT_PUBLIC_FIREBASE_API_KEY=${NEXT_PUBLIC_FIREBASE_API_KEY}
ENV NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=${NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN}
ENV NEXT_PUBLIC_FIREBASE_PROJECT_ID=${NEXT_PUBLIC_FIREBASE_PROJECT_ID}
ENV NEXT_PUBLIC_FIREBASE_APP_ID=${NEXT_PUBLIC_FIREBASE_APP_ID}
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production \
    PORT=8080 \
    HOSTNAME=0.0.0.0 \
    NEXT_TELEMETRY_DISABLED=1

RUN addgroup -S nodejs -g 1001 && adduser -S next -G nodejs -u 1001
COPY --from=build --chown=next:nodejs /app/.next/standalone ./
COPY --from=build --chown=next:nodejs /app/.next/static ./.next/static
COPY --from=build --chown=next:nodejs /app/public ./public
USER next

EXPOSE 8080
CMD ["node", "server.js"]
