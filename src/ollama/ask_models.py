"""DTO templates for conversation with the model"""

from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

class GenerationOptions(BaseModel):
    """
    Below is a breakdown of each option, what it does, and its impact on performance and resource use:

    num_keep (e.g. 5):
    This specifies how many tokens from the prompt or context to preserve without change during generation. Keeping more tokens may help maintain context in longer prompts but doesn’t add a significant compute cost.
    Example: Preserving the first five tokens of a long conversation so that they aren’t truncated.

    seed (e.g. 42):
    The random seed ensures reproducible outputs. Changing it yields different generations. It doesn’t affect speed or memory use.
    Example: Using seed 42 always produces the same text for a given prompt.

    num_predict (e.g. 100):
    Determines how many tokens the model will generate. A higher number increases output length, directly increasing processing time and memory usage.
    Example: Generating 100 tokens versus 50 tokens—double the computation.

    top_k (e.g. 20):
    In top‑k sampling, the model only considers the top 20 most probable tokens at each step. Lower values limit diversity and can speed up selection; higher values increase randomness with a slight performance hit.
    Example: Setting top_k to 20 ensures you don’t sample from low-probability (and often irrelevant) tokens.

    top_p (e.g. 0.9):
    Also known as nucleus sampling, it restricts choices to the smallest set of tokens whose cumulative probability exceeds 0.9. It balances diversity and coherence with negligible extra cost.
    Example: With top_p = 0.9, rare words are less likely to appear, keeping output on topic.

    min_p (e.g. 0.0):
    This threshold might exclude tokens below a certain probability from being sampled. It helps prune extremely unlikely options without significant impact on resources.
    Example: Setting min_p = 0.0 means there’s no lower cutoff; raising it would remove very unlikely tokens.

    typical_p (e.g. 0.7):
    Used in typical sampling, it filters tokens based on how “typical” their probability is relative to the overall distribution. This can make outputs feel more natural, with minimal additional computation.
    Example: With typical_p = 0.7, the model avoids unusual continuations that might derail coherence.

    repeat_last_n (e.g. 33):
    This tells the model to look back at the last 33 tokens to penalize repetitions. It helps reduce loops and repeated phrases. A larger window may add slight overhead in checking history.
    Example: By considering the last 33 tokens, the model avoids repeating a line verbatim.

    temperature (e.g. 0.8):
    Adjusts randomness in token selection. Lower values make output more deterministic, while higher values increase creativity. It has little direct cost.
    Example: A temperature of 0.8 provides a good balance between creativity and focus compared to a higher value like 1.2.

    repeat_penalty (e.g. 1.2):
    Applies a multiplicative penalty to tokens that have already been generated recently. It helps avoid excessive repetition with a minimal impact on speed.
    Example: A token repeated in the last few words gets its probability reduced by a factor of 1.2.

    presence_penalty (e.g. 1.5):
    Penalizes tokens for having already appeared in the text, encouraging new topics. The computational overhead is minimal.
    Example: Encouraging the model to introduce a new idea instead of rehashing the same word.

    frequency_penalty (e.g. 1.0):
    Similar to the presence penalty, but scales with how often a token appears. It keeps output varied with almost no extra cost.
    Example: Preventing a common word from being overused throughout a long output.

    mirostat (e.g. 1):
    Enables the Mirostat sampling algorithm, which dynamically controls output “surprise” (entropy) to maintain a target perplexity. It can slightly increase computation due to its iterative adjustment.
    Example: Activating mirostat can prevent sudden topic shifts by keeping perplexity near a target value.

    mirostat_tau (e.g. 0.8):
    Sets the target perplexity for Mirostat. A lower tau makes the generation more conservative.
    Example: With tau = 0.8, the algorithm aims for lower entropy, resulting in tighter, more predictable text.

    mirostat_eta (e.g. 0.6):
    Acts as the learning rate for Mirostat’s adjustments. It affects how quickly the sampling adapts to reach the target perplexity, with negligible resource impact.
    Example: A setting of 0.6 provides moderate adjustment speed—neither too slow nor too erratic.

    penalize_newline (true):
    When enabled, newline tokens are penalized, reducing the chance of excessive line breaks. This minor check can improve formatting consistency without extra resource cost.
    Example: Preventing the model from outputting several empty lines in a row.

    stop (e.g. ["\n", "user:"]):
    Specifies tokens that, when generated, will halt further output. It’s a simple check that does not notably affect performance.
    Example: Stopping generation at a newline to keep the response short.

    numa (false):
    Controls whether NUMA (Non-Uniform Memory Access) optimizations are used. Enabling it on appropriate hardware can improve memory access speed, though it requires proper system configuration.
    Example: On a multi-socket system, enabling NUMA could balance memory load, but if false, the model may run without such optimizations.

    num_ctx (e.g. 1024):
    Sets the context window size (number of tokens the model can “see” at once). A larger context improves long-form coherence but increases memory usage and computation.
    Example: A context of 1024 tokens allows for longer conversations at the cost of higher VRAM usage.

    num_batch (e.g. 2):
    Specifies how many token batches to process in parallel. Larger batches can speed up generation on capable hardware but require more memory.
    Example: Using a batch size of 2 may double throughput if GPU memory allows.

    num_gpu (e.g. 1):
    Indicates how many GPUs to use. More GPUs can reduce generation time through parallelism but obviously consume more hardware resources.
    Example: Allocating one GPU versus two can impact speed if the model supports multi-GPU scaling.

    main_gpu (e.g. 0):
    Selects the primary GPU (by index) for the generation process. It ensures that in multi-GPU systems, one is designated for main processing without affecting performance directly.
    Example: Setting main_gpu to 0 tells the system to use the first GPU for key computations.

    low_vram (false):
    When true, the system employs techniques to lower VRAM usage—often at the cost of speed. Keeping it false means the model uses full resources for maximum performance.
    Example: In a machine with limited GPU memory, enabling low_vram might allow the model to run albeit slower.

    vocab_only (false):
    Likely a debugging or initialization option where only the vocabulary is loaded (without full model weights). It minimizes resource use but is not meant for full generation tasks.
    Example: Setting vocab_only to true might be used during a lightweight check or for certain analyses.

    use_mmap (true):
    Enables memory-mapping of model files, which can reduce RAM usage by loading parts of the model on demand from disk. It generally speeds up startup without a heavy performance penalty if disk I/O is fast.
    Example: On a system with fast SSDs, use_mmap can help load a large model without consuming all system memory.

    use_mlock (false):
    When enabled, it locks model data in memory to prevent swapping. This can stabilize performance under high load but requires enough physical RAM and may need elevated privileges.
    Example: On systems with ample RAM, enabling use_mlock might prevent latency spikes due to memory swapping.

    num_thread (e.g. 8):
    Sets the number of CPU threads to use. More threads can speed up processing if the workload is CPU-bound, but using too many threads may cause contention or higher overall CPU usage.
    Example: Running with 8 threads on a multi-core CPU can speed up preprocessing steps in generation.

Each parameter offers a trade-off between quality, randomness, coherence, and computational efficiency. Adjusting them lets you fine-tune output characteristics while balancing available hardware resources.

    "options": {
      "num_keep": 5,
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
      "stop": ["\n", "user:"],
      "numa": false,
      "num_ctx": 1024,
      "num_batch": 2,
      "num_gpu": 1,
      "main_gpu": 0,
      "low_vram": false,
      "vocab_only": false,
      "use_mmap": true,
      "use_mlock": false,
      "num_thread": 8
    }
    """
    pass

class AskRequest(BaseModel):
    """
    Ollama compatible model name to use and user's prompt.

    example:
        curl http://localhost:11434/api/generate -d '{
          "model": "deepseek-r1:1.5b",
          "prompt":"Why is the sky blue?"
        }' -i
    """

    model: str = Field(..., min_length=9, max_length=50)
    prompt: str = Field(str, min_length=9, max_length=1024)
    options: Optional[GenerationOptions]


class AskResponse(BaseModel):
    """
    Intermediate model response, as indicated by 'done:false'.

    example:
        {
          "model":"deepseek-r1:1.5b",
          "created_at":"2025-02-20T22:01:10.664459Z",
          "response":" affect",
          "done":false
        }
    """
    model: str = Field(..., min_length=9, max_length=50)
    created_at: datetime
    response: str
    done: bool

    def __lt__(self, other: "AskResponse") -> bool:
        if not isinstance(other, AskResponse):
            return NotImplemented
        return self.created_at < other.created_at

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AskResponse):
            return NotImplemented
        return self.created_at == other.created_at



class AskResponseComplete(AskResponse):
    """
    Final model response as indicated by 'done:true'
        as well presence of 'done_reason' and some metrics.

    example:
        {
          "model":"deepseek-r1:1.5b",
          "created_at":"2025-02-20T22:01:10.716564Z",
          "response":"",
          "done":true,
          "done_reason":"stop",
          "context":[151644,10234,374,279,12884,6303,30,151645,151648,271,151649,271,785,1894,315,279,12884,11,476,1181,6303,11094,11,374,264,1102,315,3807,9363,3238,3786,13,3197,39020,28833,279,9237,594,16566,11,432,16211,1526,5257,13617,323,24491,279,9237,594,7329,13,1634,39020,83161,448,18730,304,279,16566,11,1741,438,23552,34615,504,279,3720,11,1493,21880,646,5240,3100,311,44477,13,1096,71816,1882,3059,304,279,2518,476,6303,1894,3881,438,330,40384,774,81002,367,1189,8697,3100,1136,10175,803,1091,2518,3100,4152,311,1181,23327,45306,13,15277,11,279,12884,7952,6303,1576,6303,3100,374,36967,1393,2518,323,18575,3100,16211,1526,803,6707,382,1986,24844,374,264,949,315,279,26829,12344,3920,315,21372,774,26443,323,279,9237,594,16566,11,892,14758,3170,9104,4682,646,7802,9434,7987,13],
          "total_duration":2143499292,
          "load_duration":30846417,
          "prompt_eval_count":9,
          "prompt_eval_duration":138000000,
          "eval_count":153,
          "eval_duration":1973000000
        }
    """
    done_reason: str
    context: List[int]
    total_duration: timedelta
    load_duration: timedelta
    prompt_eval_count: int
    prompt_eval_duration: timedelta
    eval_count: int
    eval_duration: timedelta

    @field_validator(
        'total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration', mode='before')
    def convert_nanoseconds_to_timedelta(cls, nanoseconds: int) -> timedelta:
        """Converts from model's int nanoseconds to native timedelta"""

        return timedelta(seconds=float(nanoseconds) / 1e9)
