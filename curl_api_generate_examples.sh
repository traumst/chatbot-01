# request json mode:
# https://github.com/ollama/ollama/blob/main/docs/api.md#request-json-mode
curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-r1:8b",
  "prompt": "What color is the sky at different times of the day? Respond using JSON",
  "format": "json",
  "stream": false
}'
# {
#  "model": "deepseek-r1:8b",
#  "created_at": "2023-11-09T21:07:55.186497Z",
#  "response": "{\n\"morning\": {\n\"color\": \"blue\"\n},\n\"noon\": {\n\"color\": \"blue-gray\"\n},\n\"afternoon\": {\n\"color\": \"warm gray\"\n},\n\"evening\": {\n\"color\": \"orange\"\n}\n}\n",
#  "done": true,
#  "context": [1, 2, 3],
#  "total_duration": 4648158584,
#  "load_duration": 4071084,
#  "prompt_eval_count": 36,
#  "prompt_eval_duration": 439038000,
#  "eval_count": 180,
#  "eval_duration": 4196918000
# }

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
  "model": "deepseek-r1:8b",
  "prompt": "Why is the sky blue?"
}' |
  jq --unbuffered -r '.response' |
  awk '{printf "%s", $0; fflush()}'

# /generate request options body argument
curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-r1:8b",
  "prompt": "Why is the sky blue?",
  "options": {
    "num_keep": 0,
    "seed": 42,
    "num_predict": 100,
    "top_k": 20,
    "top_p": 0.9,
    "min_p": 0.0,
    "typical_p": 0.7,
    "repeat_last_n": 33,
    "temperature": 0.8,
    "repeat_penalty": 1.2,
    "presence_penalty": 1.5,
    "frequency_penalty": 1.0,
    "mirostat": 1,
    "mirostat_tau": 0.8,
    "mirostat_eta": 0.6,
    "penalize_newline": true,
    "stop": [],
    "numa": false,
    "num_ctx": 1024,
    "num_batch": 8,
    "num_gpu": 1,
    "main_gpu": 0,
    "low_vram": true,
    "vocab_only": false,
    "use_mmap": true,
    "use_mlock": false,
    "num_thread": 8
  }
}' |
  jq --unbuffered -r '.response' |
  awk '{printf "%s", $0; fflush()}'