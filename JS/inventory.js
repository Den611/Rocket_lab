document.addEventListener('DOMContentLoaded', () => {
    // 1. Налаштування кнопки назад
    const backBtn = document.getElementById('back-btn');
    const urlParams = new URLSearchParams(window.location.search);
    const familyId = urlParams.get('family_id');

    if (familyId) {
        // Якщо є ID сім'ї, додаємо його до посилання назад
        backBtn.href = `index.html?family_id=${familyId}`;
        loadInventory(familyId);
    } else {
        // Якщо немає, пробуємо взяти дефолтний або показати помилку
        console.warn("No family_id provided!");
        document.querySelector('.loading-text').innerText = "Помилка: не знайдено ID гравця";
    }
});

async function loadInventory(familyId) {
    try {
        // ЗАПИТ ДО СЕРВЕРА (потрібно додати цей endpoint в Python)
        const response = await fetch(`/api/inventory?family_id=${familyId}`);
        const data = await response.json();

        if (data.error) {
            alert("Помилка: " + data.error);
            return;
        }

        renderResources(data.resources);
        renderModules(data.modules);

    } catch (e) {
        console.error("Connection error:", e);
        document.getElementById('resources-grid').innerHTML = '<div style="color:red">Помилка з\'єднання з сервером</div>';
    }
}

function renderResources(res) {
    const container = document.getElementById('resources-grid');
    container.innerHTML = '';

    // Список ресурсів (можна розширити)
    const items = [
        { key: 'iron', name: 'Залізо', icon: '🔩', color: '#aebbc9' },
        { key: 'fuel', name: 'Паливо', icon: '💠', color: '#ff9d00' },
        { key: 'coins', name: 'Спейскоіни', icon: '🪙', color: '#00ff9d' },
        { key: 'energy', name: 'Енергія', icon: '⚡', color: '#00f2ff' } // Приклад додаткового
    ];

    items.forEach(item => {
        // Якщо ресурс прийшов з сервера, показуємо його
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

function renderModules(modules) {
    const container = document.getElementById('modules-grid');
    container.innerHTML = '';

    if (!modules || modules.length === 0) {
        container.innerHTML = '<div style="color:gray; padding:10px;">Ангар порожній. Досліджуйте технології!</div>';
        return;
    }

    modules.forEach(mod => {
        const card = document.createElement('div');
        card.className = 'mod-card';
        
        // Вибираємо картинку (можна додати логіку для різних картинок)
        let imgPath = 'images/modules/placeholder.png';
        if (mod.type === 'nose') imgPath = 'images/Nose.png';
        if (mod.type === 'body') imgPath = 'images/Korpus.png';
        if (mod.type === 'engine') imgPath = 'images/Turbina.png';
        if (mod.type === 'fins') imgPath = 'images/Stabilizator.png';

        card.innerHTML = `
            <div class="mod-img-box">
                <img src="${imgPath}" alt="${mod.name}">
            </div>
            <div class="mod-body">
                <span class="mod-tier">TIER ${mod.tier || 'I'}</span>
                <h3 class="mod-name">${mod.name}</h3>
                <p class="mod-desc">${mod.desc || 'Високотехнологічний модуль для вашої ракети.'}</p>
            </div>
        `;
        container.appendChild(card);
    });
}