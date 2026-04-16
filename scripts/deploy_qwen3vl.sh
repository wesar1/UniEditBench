# Qwen3-VL-4B Image lora
CUDA_VISIBLE_DEVICES=0 swift deploy \
    --model /path/to/Qwen3-VL-4B-Instruct \
    --adapters /path/to/sft_image_lora_4b \
    --device_map balanced \
    --vllm_tensor_parallel_size 1 \
    --attn_impl eager \
    --infer_backend vllm \
    --port 8003 \
    --vllm_max_lora_rank 32 \
    --max_new_tokens 2048 \
    --served_model_name Qwen3-VL-4B-SFT-Image

# Qwen3-VL-8B Image lora
CUDA_VISIBLE_DEVICES=1 swift deploy \
    --model /path/to/Qwen3-VL-8B-Instruct \
    --adapters /path/to/sft_image_lora_8b \
    --device_map balanced \
    --vllm_tensor_parallel_size 1 \
    --attn_impl eager \
    --infer_backend vllm \
    --port 8004 \
    --vllm_max_lora_rank 32 \
    --max_new_tokens 2048 \
    --served_model_name Qwen3-VL-8B-SFT-Image

# Qwen3-VL-4B Image+Video lora
CUDA_VISIBLE_DEVICES=2 swift deploy \
    --model /path/to/Qwen3-VL-4B-Instruct \
    --adapters /path/to/sft_image_video_lora_4b \
    --device_map balanced \
    --vllm_tensor_parallel_size 1 \
    --attn_impl eager \
    --infer_backend vllm \
    --port 8005 \
    --vllm_max_lora_rank 32 \
    --max_new_tokens 2048 \
    --served_model_name Qwen3-VL-4B-SFT-Image+Video

# Qwen3-VL-8B Image+Video lora
CUDA_VISIBLE_DEVICES=3 swift deploy \
    --model /path/to/Qwen3-VL-8B-Instruct \
    --adapters /path/to/sft_image_video_lora_8b \
    --device_map balanced \
    --vllm_tensor_parallel_size 1 \
    --attn_impl eager \
    --infer_backend vllm \
    --port 8006 \
    --vllm_max_lora_rank 32 \
    --max_new_tokens 2048 \
    --served_model_name Qwen3-VL-8B-SFT-Image+Video