document.addEventListener("DOMContentLoaded", () => {
    console.log('🚀 Rocket Lab System Initialized');

    // Ініціалізація ефектів
    initHyperSpace();
    initNavigation();
    initInteractions();

    // Запуск синхронізації з сервером
    if (typeof GLOBAL_FAMILY_ID !== 'undefined' && GLOBAL_FAMILY_ID) {
        syncData();
        setInterval(syncData, 5000); // Оновлення кожні 5 сек
    } else {
        console.error("Critical: Family ID missing!");
    }

    // Розгортання Telegram WebApp
    if (window.Telegram && window.Telegram.WebApp) {
        window.Telegram.WebApp.expand();
    }
});

// --- СИНХРОНІЗАЦІЯ З СЕРВЕРОМ ---
async function syncData() {
    if (!GLOBAL_FAMILY_ID) return;

    try {
        // 1. Оновлення ресурсів
        const resInventory = await fetch(`/api/inventory?family_id=${GLOBAL_FAMILY_ID}`);
        const dataInv = await resInventory.json();

        if (dataInv.resources) {
            updateText('val-iron', dataInv.resources.iron);
            updateText('val-fuel', dataInv.resources.fuel);
            updateText('val-coins', dataInv.resources.coins);
        }

        // 2. Оновлення модулів ракети (візуалізація)
        const resUpgrades = await fetch(`/api/get_upgrades?family_id=${GLOBAL_FAMILY_ID}`);
        const unlockedModules = await resUpgrades.json(); // Прийде масив ['nose', 'body1', ...]

        updateRocketVisuals(unlockedModules);

    } catch (e) {
        console.error("Sync Error:", e);
    }
}

function updateText(id, val) {
    const el = document.getElementById(id);
    if (el) el.innerText = val;
}

// --- ВІЗУАЛІЗАЦІЯ РАКЕТИ ---
function updateRocketVisuals(unlockedList) {
    // Список всіх можливих типів модулів на сторінці
    const moduleTypes = ['nose', 'body', 'engine', 'fins', 'cabin', 'cargo', 'solar', 'booster'];

    moduleTypes.forEach(type => {
        const elements = document.querySelectorAll(`[data-module="${type}"]`);

        // Перевіряємо, чи є у нас модуль цього типу в списку куплених
        // Наприклад, якщо unlockedList містить 'nose' або 'nose_mk2'
        const isOwned = unlockedList.some(id => id.startsWith(type) || id === type);

        elements.forEach(el => {
            if (isOwned) {
                el.style.display = 'block';
                el.classList.add('tier-1'); // Можна додати логіку рівнів, якщо IDs містять рівень
            } else {
                // Якщо це не базовий модуль (як body), ховаємо
                // Але body зазвичай має бути завжди, тому перевіримо
                if (type === 'body') el.style.display = 'block';
                else el.style.display = 'none';
            }
        });
    });
}

// --- НАВІГАЦІЯ ---
function initNavigation() {
    // 1. Планети (використовуємо глобальну функцію)
    document.querySelectorAll('.planet-item').forEach(item => {
        item.addEventListener('click', () => {
            const name = item.querySelector('.planet-name').innerText.trim();
            switch(name) {
                case 'EARTH': window.navigateTo('index.html'); break;
                case 'MOON': window.navigateTo('Moon.html'); break;
                case 'MARS': window.navigateTo('Mars.html'); break;
                case 'JUPITER': window.navigateTo('Jupiter.html'); break;
            }
        });
    });

    // 2. Кнопка Дерева
    const treeBtn = document.querySelector('.tech-tree-btn');
    if (treeBtn) {
        treeBtn.addEventListener('click', () => {
            window.navigateTo('tree_Earth.html');
        });
    }

    // 3. Інвентар
    const invBtn = document.querySelector('.inventory-sq');
    if (invBtn) {
        invBtn.addEventListener('click', () => {
            window.navigateTo('inventory.html');
        });
    }
}

// --- ІНФО ПАНЕЛЬ ---
function initInteractions() {
    const modules = document.querySelectorAll('.module');
    const panel = document.getElementById('infoPanel');
    const btn = document.querySelector('.upgrade-btn');

    // Кнопка в панелі тепер веде в дерево розробок
    if (btn) {
        btn.innerText = "GO TO RESEARCH";
        btn.addEventListener('click', () => {
            window.navigateTo('tree_Earth.html');
        });
    }

    modules.forEach(mod => {
        mod.addEventListener('mouseenter', () => {
            const key = mod.getAttribute('data-module');
            refreshInfoPanel(key);
            panel.classList.add('active');
        });
    });
}

const MODULE_INFO = {
    nose: { title: "Nose Cone", desc: "Aerodynamic fairing." },
    body: { title: "Fuel Tank", desc: "Main propellant storage." },
    engine: { title: "Rocket Engine", desc: "High thrust propulsion." },
    fins: { title: "Stabilizers", desc: "Aerodynamic control." },
    // Додайте інші...
};

function refreshInfoPanel(key) {
    const info = MODULE_INFO[key] || { title: "Unknown Module", desc: "No data available." };
    const pTitle = document.getElementById('panelTitle');
    const pDesc = document.getElementById('panelDesc');

    if (pTitle) pTitle.innerText = info.title.toUpperCase();
    if (pDesc) pDesc.innerText = info.desc;
}

// --- ФОНОВІ ЗІРКИ ---
function initHyperSpace() {
    const container = document.getElementById('space-container');
    if (!container) return;
    container.innerHTML = '';

    for (let i = 0; i < 150; i++) {
        const star = document.createElement('div');
        star.classList.add('star');
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`; // Додано random top

        const size = Math.random() * 2 + 1;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.animationDuration = `${Math.random() * 3 + 2}s`;
        star.style.animationDelay = `-${Math.random() * 5}s`;

        container.appendChild(star);
    }
}