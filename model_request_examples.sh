curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-r1:8b",
  "prompt":"Why is the sky blue?"
}'

curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-r1:8b",
  "prompt": "Why is the sky blue?"
}' |
  jq -r '.response'

curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-r1:1.5b",
  "prompt": "Why is the sky blue?"
}' |
  jq --unbuffered -r '.response' |
  awk '{printf "%s", $0; fflush()}'