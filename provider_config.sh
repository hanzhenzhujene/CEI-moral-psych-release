#!/usr/bin/env bash
# Provider routing config for benchmark runner.
# Maps OpenRouter model IDs to alternative providers (Ark, DeepSeek, etc.)
# Models not listed here fall back to OpenRouter.
#
# To add a new provider:
#   1. Add a case to resolve_provider() with "provider|model_id"
#   2. Add URL to provider_url()
#   3. Add env var name to provider_key_var()
#   4. Add the API key to .env

# resolve_provider MODEL_ID
# Echoes: PROVIDER|PROVIDER_MODEL_ID
# Returns 1 if no mapping (fallback to OpenRouter).
resolve_provider() {
    case "$1" in
        # Volcengine Ark models
        # NOTE: Update these with endpoint IDs (ep-xxx) after creating endpoints
        # in the Ark console: https://cloud.bytedance.net/ark/region:ark+cn-beijing/endpoint
        "qwen/qwen3-8b")              echo "dashscope|qwen3-8b" ;;
        "qwen/qwen3-32b")             echo "ark|qwen3-32b-20250429" ;;
        "deepseek/deepseek-chat-v3.1") echo "ark|deepseek-v3-2-251201" ;;

        # Together AI — cheaper than OpenRouter for this model
        "qwen/qwen3-235b-a22b") echo "together|Qwen/Qwen3-235B-A22B-Instruct-2507-tput" ;;

        # Google AI Studio — free for Gemma models
        "google/gemma-3-4b-it")   echo "google|gemma-3-4b-it" ;;
        "google/gemma-3-12b-it")  echo "google|gemma-3-12b-it" ;;
        "google/gemma-3-27b-it")  echo "google|gemma-3-27b-it" ;;

        # DeepSeek direct API — cheaper than OpenRouter
        "deepseek/deepseek-r1")                    echo "deepseek|deepseek-reasoner" ;;
        "deepseek/deepseek-r1-distill-llama-70b")  echo "deepseek|deepseek-r1-distill-llama-70b" ;;

        # MiniMax direct API — bypasses OpenRouter issues and uses the funded
        # account for both text and SMID vision routes.
        # MiniMax image-understanding cookbook currently routes through
        # MiniMax-Text-01 with the image embedded as base64 text because the
        # OpenAI-compatible endpoint rejects image_url content blocks.
        "minimax/minimax-01") echo "minimax|MiniMax-Text-01" ;;
        "minimax/minimax-m2.5") echo "minimax|MiniMax-M2.5" ;;

        *) return 1 ;;
    esac
}

provider_url() {
    case "$1" in
        ark)        echo "https://ark.cn-beijing.volces.com/api/v3" ;;
        together)   echo "https://api.together.xyz/v1" ;;
        deepseek)   echo "https://api.deepseek.com" ;;
        google)     echo "https://generativelanguage.googleapis.com/v1beta/openai" ;;
        minimax)    echo "https://api.minimax.io/v1" ;;
        dashscope)  echo "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" ;;
        openrouter) echo "https://openrouter.ai/api/v1" ;;
        *)          echo "https://openrouter.ai/api/v1" ;;
    esac
}

provider_key_var() {
    case "$1" in
        ark)        echo "ARK_API_KEY" ;;
        together)   echo "TOGETHER_API_KEY" ;;
        deepseek)   echo "DEEPSEEK_API_KEY" ;;
        google)     echo "GOOGLE_API_KEY" ;;
        minimax)    echo "MINIMAX_API_KEY" ;;
        dashscope)  echo "DASHSCOPE_API_KEY" ;;
        openrouter) echo "OPENROUTER_API_KEY" ;;
        *)          echo "OPENROUTER_API_KEY" ;;
    esac
}

# setup_model_provider MODEL_ID
# Sets: EFFECTIVE_MODEL, OPENAI_API_KEY, OPENAI_BASE_URL
# Usage: setup_model_provider "qwen/qwen3-8b"
setup_model_provider() {
    local model="$1"
    local entry

    if entry=$(resolve_provider "$model"); then
        local provider="${entry%%|*}"
        local provider_model="${entry#*|}"
        local key_var
        key_var=$(provider_key_var "$provider")

        EFFECTIVE_MODEL="$provider_model"
        export OPENAI_BASE_URL
        OPENAI_BASE_URL=$(provider_url "$provider")

        # Resolve the key variable indirectly (eval for bash 3.2 compat).
        # Use the `${var-}` form so launchers running with `set -u` can still
        # preflight missing provider keys without crashing in the router itself.
        eval "export OPENAI_API_KEY=\"\${$key_var-}\""

        echo "  [provider] $model → $provider ($provider_model)" >&2
    else
        EFFECTIVE_MODEL="$model"
        export OPENAI_API_KEY="${OPENROUTER_API_KEY:-}"
        export OPENAI_BASE_URL="https://openrouter.ai/api/v1"

        echo "  [provider] $model → openrouter" >&2
    fi
}
