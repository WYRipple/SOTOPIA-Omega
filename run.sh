python -m vllm.entrypoints.openai.api_server  \
    --served-model-name Qwen25-7B-Instruct \
    --model /root/autodl-tmp/LLM_model/Qwen2.5-7B-Instruct \
    --tensor-parallel-size 4