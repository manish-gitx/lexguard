#!/usr/bin/env bash
set -euo pipefail

PROJECT="$(gcloud config get-value project 2>/dev/null)"
REGION="${REGION:-asia-south1}"
SERVICE="lexguard-web"
API_URL="${NEXT_PUBLIC_LEXGUARD_API_URL:-https://lexguard-api-3mvnlmbu5q-el.a.run.app}"
FIREBASE_API_KEY="${NEXT_PUBLIC_FIREBASE_API_KEY:-}"
FIREBASE_AUTH_DOMAIN="${NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN:-}"
FIREBASE_PROJECT_ID="${NEXT_PUBLIC_FIREBASE_PROJECT_ID:-}"
FIREBASE_APP_ID="${NEXT_PUBLIC_FIREBASE_APP_ID:-}"

if [[ -z "${PROJECT}" || "${PROJECT}" == "(unset)" ]]; then
  echo "error: no active gcloud project." >&2
  exit 1
fi

echo "deploying ${SERVICE} to ${REGION} on ${PROJECT}"
echo "api url   : ${API_URL}"

cd "$(dirname "$0")/.."  # website/

gcloud run deploy "${SERVICE}" \
  --source . \
  --region "${REGION}" \
  --project "${PROJECT}" \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 2 \
  --concurrency 80 \
  --timeout 60 \
  --port 8080 \
  --set-build-env-vars "NEXT_PUBLIC_LEXGUARD_API_URL=${API_URL},NEXT_PUBLIC_FIREBASE_API_KEY=${FIREBASE_API_KEY},NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=${FIREBASE_AUTH_DOMAIN},NEXT_PUBLIC_FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID},NEXT_PUBLIC_FIREBASE_APP_ID=${FIREBASE_APP_ID}" \
  --set-env-vars "NEXT_PUBLIC_LEXGUARD_API_URL=${API_URL},NEXT_PUBLIC_FIREBASE_API_KEY=${FIREBASE_API_KEY},NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=${FIREBASE_AUTH_DOMAIN},NEXT_PUBLIC_FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID},NEXT_PUBLIC_FIREBASE_APP_ID=${FIREBASE_APP_ID}" \
  --quiet

URL="$(gcloud run services describe "${SERVICE}" \
  --region "${REGION}" --project "${PROJECT}" \
  --format='value(status.url)')"

echo ""
echo "deployed: ${URL}"
