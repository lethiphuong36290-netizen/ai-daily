#!/usr/bin/env python3
"""
AI Daily 自动更新脚本
每天定时运行：aihot新闻 + MiniMax音乐 + MiniMax图片 → 推送到GitHub
"""
import urllib.request, json, os, base64, subprocess
from datetime import datetime

# ========== 配置 ==========
REPO_DIR = "/tmp/ai-daily"
ENV_FILE = "/home/txf_1128/.hermes/.env"
MINIMAX_API_KEY = None
GITHUB_TOKEN = None

# 加载 API Key
with open(ENV_FILE) as f:
    for line in f:
        if not line.strip() or line.startswith("#"):
            continue
        if "MINIMAX_CN_API_KEY" in line:
            MINIMAX_API_KEY = line.split("=", 1)[1].strip().strip('"')
        elif "GITHUB_TOKEN" in line:
            GITHUB_TOKEN = line.split("=", 1)[1].strip().strip('"')

BASE_URL = "https://api.minimaxi.chat"
HEADERS = {"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"}

os.makedirs(f"{REPO_DIR}/music", exist_ok=True)
os.makedirs(f"{REPO_DIR}/images", exist_ok=True)

now = datetime.utcnow()
date_str = now.strftime("%Y-%m-%d")
ts = now.strftime("%Y%m%d_%H%M%S")

def api_post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())

def git_commit_push(msg):
    # 把 token 注入 git remote，避免交互式认证
    remote_url = f"https://{GITHUB_TOKEN}@github.com/lethiphuong36290-netizen/ai-daily.git"
    subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=REPO_DIR, check=False)
    cmds = [
        ["git", "add", "-A"],
        ["git", "commit", "-m", msg],
        ["git", "push", "origin", "main"]
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"Git error: {r.stderr}")
            raise SystemExit(1)

# ========== 1. 获取 aihot 新闻 ==========
print("📰 获取 aihot 新闻...")
try:
    req = urllib.request.Request(
        "https://aihot.virxact.com/api/public/items?mode=selected&take=3",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = json.loads(resp.read())
    news_items = []
    for item in raw.get("items", []):
        pub = item.get("publishedAt", "")[:10]
        news_items.append({
            "category": item.get("category", "资讯"),
            "title": item.get("title", ""),
            "description": item.get("summary", "")[:200],
            "source": item.get("source", ""),
            "date": pub,
            "url": item.get("url", "")
        })
    print(f"  获取到 {len(news_items)} 条新闻")
except Exception as e:
    print(f"  aihot 获取失败: {e}，使用默认数据")
    news_items = [{
        "category": "资讯", "title": "AI 技术持续改变各行各业",
        "description": "最新AI应用在各行业加速落地",
        "source": "AI Daily", "date": date_str, "url": ""
    }]

# ========== 2. 生成 2 首音乐 ==========
print("🎵 生成音乐...")
music_items = []
music_prompts = [
    {
        "name": f"track{ts}_ambient.mp3",
        "prompt": "Chill ambient electronic music, dreamy synth pads, slow arpeggios, relaxed atmosphere, late night listening",
        "lyrics": "[Verse 1]\n城市霓虹在闪烁\n数字浪潮轻轻拍打\n\n[Chorus]\n在光的缝隙里\n听见未来的呼吸\n\n[Verse 2]\n代码如星河蔓延\n创意的火花在跳跃\n\n[Chorus]\n每一个音符\n都是一束光"
    },
    {
        "name": f"track{ts}_poprock.mp3",
        "prompt": "Upbeat pop rock, energetic guitars, driving drums, motivational and inspiring",
        "lyrics": "[Verse 1]\n黎明破晓的那一刻\n我们踏上了旅程\n\n[Verse 2]\n不惧风雨的阻挡\n每一次尝试都是新起点\n\n[Chorus]\n这就是我们的声音\n用旋律编织梦想\n让代码插上翅膀"
    }
]

for m in music_prompts:
    try:
        data = api_post(f"{BASE_URL}/v1/music_generation", {
            "model": "music-2.6",
            "prompt": m["prompt"],
            "lyrics": m["lyrics"]
        })
        if data["base_resp"]["status_code"] == 0:
            path = f"{REPO_DIR}/music/{m['name']}"
            with open(path, "wb") as f:
                f.write(bytes.fromhex(data["data"]["audio"]))
            size = os.path.getsize(path)
            print(f"  ✅ {m['name']} ({size//1024}KB)")
            music_items.append({
                "title": m["name"].replace(".mp3", "").replace(f"track{ts}_", "AI音乐 · "),
                "description": m["prompt"][:50],
                "url": f"music/{m['name']}",
                "date": date_str
            })
        else:
            print(f"  ❌ 音乐生成失败: {data}")
    except Exception as e:
        print(f"  ❌ 音乐异常: {e}")

# ========== 3. 生成 2 张图片 ==========
print("🎨 生成图片...")
image_items = []
image_prompts = [
    {
        "name": f"img{ts}_city.jpg",
        "prompt": "Futuristic digital city at night, neon lights reflecting on rain-wet streets, cyberpunk aesthetic, holographic AI icons floating, epic wide shot, cinematic lighting, 8k quality",
        "ratio": "16:9"
    },
    {
        "name": f"img{ts}_neural.jpg",
        "prompt": "Abstract visualization of artificial intelligence, glowing neural network pathways in deep blue and purple, human silhouette made of light circuits, cosmic background, futuristic atmosphere, 8k quality",
        "ratio": "16:9"
    }
]

for img in image_prompts:
    try:
        data = api_post(f"{BASE_URL}/v1/image_generation", {
            "model": "image-01",
            "prompt": img["prompt"],
            "aspect_ratio": img["ratio"],
            "response_format": "base64"
        })
        img_b64 = data["data"]["image_base64"][0]
        path = f"{REPO_DIR}/images/{img['name']}"
        with open(path, "wb") as f:
            f.write(base64.b64decode(img_b64))
        size = os.path.getsize(path)
        print(f"  ✅ {img['name']} ({size//1024}KB)")
        image_items.append({
            "title": img["name"].replace(f"img{ts}_", "").replace(".jpg", "").replace("_", " ").title(),
            "description": img["prompt"][:80],
            "url": f"images/{img['name']}",
            "date": date_str
        })
    except Exception as e:
        print(f"  ❌ 图片异常: {e}")

# ========== 4. 更新 data.json 并推送 ==========
print("📦 更新 data.json...")

# 保留现有的图片/音乐（不追加新生成的，只更新新闻）
data_path = f"{REPO_DIR}/data/data.json"
if os.path.exists(data_path):
    with open(data_path) as f:
        existing = json.load(f)
    # 合并：取最新的各2条
    existing_imgs = existing.get("images", [])[:2]
    existing_music = existing.get("music", [])[:2]
else:
    existing_imgs = []
    existing_music = []

new_data = {
    "updateTime": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "news": news_items,
    "images": image_items or existing_imgs,
    "music": music_items or existing_music
}

with open(data_path, "w", encoding="utf-8") as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)

print(f"  新闻 {len(new_data['news'])} 条 | 图片 {len(new_data['images'])} 张 | 音乐 {len(new_data['music'])} 首")

print("🚀 推送到 GitHub...")
git_commit_push(f"Auto update: {date_str} {now.strftime('%H:%M')} - {len(new_data['news'])}条新闻")
print("✅ 更新完成!")
