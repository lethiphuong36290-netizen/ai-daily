#!/bin/bash
# AI Daily 自动更新脚本
# 每天定时运行，收集新闻并推送到 GitHub

DATE=$(date +%Y-%m-%d)
echo "开始更新 AI Daily - $DATE"

# 1. 拉取最新代码
cd /tmp/ai-daily
git pull origin main

# 2. 更新新闻数据 (示例，实际由 Hermes Agent 调用 aihot API)
# 这里写入静态新闻数据
cat > data/data.json << 'DATA'
{
    "updateTime": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "news": [
        {
            "category": "行业动态",
            "title": "AI 技术持续改变各行各业",
            "description": "最新AI应用在各行业加速落地",
            "source": "AI Daily",
            "date": "$DATE"
        }
    ],
    "images": [],
    "music": []
}
DATA

# 3. 提交并推送
git add .
git commit -m "Auto update: $DATE"
git push origin main

echo "更新完成 - $DATE"
