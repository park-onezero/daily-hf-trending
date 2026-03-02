import requests
import os

SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")

def format_params(param_count):
    if not param_count: return "-"
    if param_count >= 1e9: return f"{param_count / 1e9:.1f}B"
    if param_count >= 1e6: return f"{param_count / 1e6:.1f}M"
    return str(param_count)

def format_bytes(size_bytes):
    if not size_bytes: return "-"
    if size_bytes >= 1024**3: return f"{size_bytes / 1024**3:.1f}GB"
    if size_bytes >= 1024**2: return f"{size_bytes / 1024**2:.1f}MB"
    return str(size_bytes)

def notify_slack(model_id, summary, info):
    likes = info.get("likes", 0)
    tag = info.get("pipeline_tag", "-")
    
    # Extract sizes
    params = info.get("safetensors", {}).get("total")
    storage = info.get("usedStorage")
    
    param_str = format_params(params)
    storage_str = format_bytes(storage)
    
    msg = f"🆕 *신규 트렌딩 모델 감지*\n*{model_id}*\n태스크: {tag} | 좋아요: {likes} | 파라미터: {param_str} | 크기: {storage_str}\n\n{summary}\n🔗 https://huggingface.co/{model_id}"
    requests.post(SLACK_WEBHOOK, json={"text": msg})
