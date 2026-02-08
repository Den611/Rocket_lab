document.addEventListener('DOMContentLoaded', () => {
    // 1. Налаштування ідентифікації та кнопки назад
    const backBtn = document.getElementById('back-btn');
    const urlParams = new URLSearchParams(window.location.search);
    const familyId = urlParams.get('family_id');

    if (familyId) {
        // Додаємо ID сім'ї до посилання назад для збереження контексту
        backBtn.href = `index.html?family_id=${familyId}`;
        loadInventory(familyId);
    } else {
        console.warn("No family_id provided!");
        const loadingText = document.querySelector('.loading-text');
        if (loadingText) loadingText.innerText = "Помилка: не знайдено ID гравця";
    }
});

/**
 * Завантажує дані інвентарю з сервера
 */
async function loadInventory(familyId) {
    try {
        // Виконуємо запит до вашого Flask API
        const response = await fetch(`/api/inventory?family_id=${familyId}`);
        
        if (!response.ok) {
            throw new Error(`Server status: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            alert("Помилка сервера: " + data.error);
            return;
        }

        // Відображаємо отримані дані
        renderResources(data.resources);
        renderModules(data.modules);

    } catch (e) {
        console.error("Connection error:", e);
        const grid = document.getElementById('resources-grid');
        if (grid) {
            grid.innerHTML = '<div style="color:red; padding:20px;">Помилка з\'єднання з бортовим комп\'ютером</div>';
        }
    }
}

/**
 * Відображає сітку ресурсів (валюта + матеріали)
 */
function renderResources(res) {
    const container = document.getElementById('resources-grid');
    if (!container) return;
    
    container.innerHTML = '';

    // Повний список ресурсів згідно зі структурою вашої БД
    const resourceMap = [
        { key: 'coins', name: 'Спейскоіни', icon: '🪙', color: '#00ff9d' },
        { key: 'iron', name: 'Залізо', icon: '🔩', color: '#aebbc9' },
        { key: 'fuel', name: 'Паливо', icon: '💠', color: '#ff9d00' },
        { key: 'regolith', name: 'Реголіт', icon: '🌑', color: '#8e8e8e' },
        { key: 'he3', name: 'Гелій-3', icon: '💎', color: '#00f2ff' },
        { key: 'silicon', name: 'Кремній', icon: '💾', color: '#32a852' },
        { key: 'oxide', name: 'Оксид', icon: '🧪', color: '#a83232' },
        { key: 'hydrogen', name: 'Водень', icon: '🎈', color: '#3262a8' },
        { key: 'helium', name: 'Гелій', icon: '🌌', color: '#6a32a8' }
    ];

    resourceMap.forEach(item => {
        // Перевіряємо наявність ресурсу в об'єкті (може бути 0, тому перевіряємо на undefined)
        if (res[item.key] !== undefined) {
            const card = document.createElement('div');
            card.className = 'res-card';
            card.style.borderColor = item.color; 
            card.innerHTML = `
                <div class="res-icon">${item.icon}</div>
                <div class="res-info">
                    <span class="res-name">${item.name}</span>
                    <span class="res-amount" style="color:${item.color}">${res[item.key]}</span>
                </div>
            `;
            container.appendChild(card);
        }
    });
}

/**
 * Відображає список розблокованих модулів в ангарі
 */
function renderModules(modules) {
    const container = document.getElementById('modules-grid');
    if (!container) return;

    container.innerHTML = '';

    if (!modules || modules.length === 0) {
        container.innerHTML = '<div style="color:gray; padding:20px; text-align:center; width:100%;">Ангар порожній. Досліджуйте нові технології в дереві розвитку!</div>';
        return;
    }

    modules.forEach(mod => {
        const card = document.createElement('div');
        card.className = 'mod-card';
        
        // Визначення шляху до зображення на основі типу модуля
        let imgPath = 'images/modules/placeholder.png';
        if (mod.type === 'nose') imgPath = 'images/Nose.png';
        if (mod.type === 'body') imgPath = 'images/Korpus.png';
        if (mod.type === 'engine') imgPath = 'images/Turbina.png';
        if (mod.type === 'fins') imgPath = 'images/Stabilizator.png';

        card.innerHTML = `
            <div class="mod-img-box">
                <img src="${imgPath}" alt="${mod.name}" onerror="this.src='images/Logo_for_site.png'">
            </div>
            <div class="mod-body">
                <div class="mod-header">
                    <span class="mod-tier">TIER ${mod.tier || 'I'}</span>
                    <span class="mod-type-label">${mod.type.toUpperCase()}</span>
                </div>
                <h3 class="mod-name">${mod.name}</h3>
                <p class="mod-desc">${mod.desc || 'Спеціалізований модуль космічної програми.'}</p>
            </div>
        `;
        container.appendChild(card);
    });
}