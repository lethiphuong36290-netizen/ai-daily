// 加载数据
async function loadData() {
    try {
        const response = await fetch('data/data.json');
        const data = await response.json();
        
        // 更新时间
        document.getElementById('update-time').textContent = new Date(data.updateTime).toLocaleString('zh-CN');
        
        // 渲染新闻
        renderNews(data.news);
        
        // 渲染图片
        renderImages(data.images);
        
        // 渲染音乐
        renderMusic(data.music);
    } catch (e) {
        console.error('加载数据失败:', e);
    }
}

function renderNews(news) {
    const container = document.getElementById('news-list');
    if (!news || news.length === 0) {
        container.innerHTML = '<p class="loading">暂无新闻</p>';
        return;
    }
    
    container.innerHTML = news.map(item => `
        <div class="news-card">
            <span class="news-category category-${item.category}">${item.category}</span>
            <h3 class="news-title"><a href="${item.url || '#'}" target="_blank">${item.title}</a></h3>
            <p class="news-desc">${item.description || ''}</p>
            <p class="news-meta">${item.source || ''} ${item.date || ''}</p>
        </div>
    `).join('');
}

function renderImages(images) {
    const container = document.getElementById('image-gallery');
    if (!images || images.length === 0) {
        container.innerHTML = '<p class="loading">暂无图片</p>';
        return;
    }
    
    container.innerHTML = images.map(item => `
        <div class="gallery-item">
            <img src="${item.url}" alt="${item.title || 'AI图片'}">
            <p>${item.title || 'AI生成图片'} - ${item.date || ''}</p>
        </div>
    `).join('');
}

function renderMusic(music) {
    const container = document.getElementById('music-list');
    if (!music || music.length === 0) {
        container.innerHTML = '<p class="loading">暂无音乐</p>';
        return;
    }
    
    container.innerHTML = music.map(item => `
        <div class="music-card">
            <h3>${item.title || 'AI音乐'}</h3>
            <p>${item.description || ''}</p>
            <audio controls src="${item.url}"></audio>
        </div>
    `).join('');
}

// 页面加载时获取数据
document.addEventListener('DOMContentLoaded', loadData);
