const canvas = document.getElementById('canvas');
const viewport = document.getElementById('viewport');
const urlParams = new URLSearchParams(window.location.search);
window.userFamilyId = urlParams.get('family_id');

let currentX = 0; 
let currentY = 0; 
let isDragging = false;
let startX, startY;
let scale = 1;
const MIN_SCALE = 0.3;
const MAX_SCALE = 3.0;
const NODE_WIDTH = 150;
const NODE_HEIGHT = 145;

let selectedNode = null;

const treeNodes = [
    // =======================================================
    // === ГРУПА 1: КОРПУС ТА МОДУЛІ (Основна гілка) ===
    // Послідовність: Корпус -> Новий Корпус -> (Розвилка: Сонячні панелі АБО Бойовий відсік)
    // =======================================================
    
    // 1. Старт (Корпус)
    { 
        id: 'hull_start', name: 'Герметизація', tier: 'I', desc: 'Покращена ізоляція відсіку для захисту вантажу.', 
        x: 1000, y: 1000, 
        req: null, owned: true, img: 'images/Korpus.png',
        cost: { iron: 0, fuel: 0, coins: 0 }
    },
    // 2. Новий Корпус (Загальний етап)
    { 
        id: 'hull_mk2', name: 'Композитний Корпус', tier: 'II', desc: 'Полегшений сплав, що дозволяє нести більше обладнання.', 
        x: 1250, y: 1000, 
        req: 'hull_start', owned: false, img: 'images/Korpus.png',
        cost: { iron: 700, fuel: 300, coins: 550 }
    },

    // --- ГІЛКА А: ЕНЕРГЕТИКА (Сонячні панелі) ---
    { 
        id: 'solar_upg', name: 'Фотоелементи MK-2', tier: 'III', desc: 'Покращення ефективності збору енергії на 50%.', 
        x: 1500, y: 850, // Вгору від корпусу
        req: 'hull_mk2', owned: false, img: 'images/Bataries.png',
        cost: { iron: 400, fuel: 200, coins: 600 }
    },
    { 
        id: 'solar_max', name: 'Квантові Панелі', tier: 'IV', desc: 'Найкраща система поглинання світла. Майже нескінченна енергія.', 
        x: 1750, y: 850, // Продовження верхньої гілки
        req: 'solar_upg', owned: false, img: 'images/Bataries.png',
        cost: { iron: 200, fuel: 500, coins: 800 }
    },

    // --- ГІЛКА Б: БОЙОВА (Відсіки та Гармати) ---
    { 
        id: 'aux_bay', name: 'Допоміжні Відсіки', tier: 'III', desc: 'Розширення простору для встановлення спецобладнання.', 
        x: 1500, y: 1150, // Вниз від корпусу
        req: 'hull_mk2', owned: false, img: 'images/Korpus.png',
        cost: { iron: 600, fuel: 200, coins: 500 }
    },
    { 
        id: 'combat_bay', name: 'Бойовий Модуль', tier: 'IV', desc: 'Броньований відсік з системою наведення.', 
        x: 1750, y: 1150, 
        req: 'aux_bay', owned: false, img: 'images/Korpus.png',
        cost: { iron: 800, fuel: 300, coins: 750 }
    },
    { 
        id: 'cannons', name: 'Плазмові Гармати', tier: 'V', desc: 'Важке озброєння для знищення астероїдів та ворогів.', 
        x: 2000, y: 1150, // Фінал нижньої гілки
        req: 'combat_bay', owned: false, img: 'images/Blasters.png',
        cost: { iron: 500, fuel: 400, coins: 1000 }
    },


    // =======================================================
    // === ГРУПА 2: ДВИГУНИ (Турбіна) ===
    // Послідовність: Турбіна -> (Розвилка: Найкраща турбіна АБО Бокові турбіни)
    // =======================================================

    // 1. Старт (Турбіна)
    { 
        id: 'eng_start', name: 'Форсаж', tier: 'I', desc: 'Базова оптимізація камери згоряння.', 
        x: 1000, y: 1500, 
        req: null, owned: true, img: 'images/Turbina.png',
        cost: { iron: 0, fuel: 0, coins: 0 }
    },

    // --- ГІЛКА А: ГОЛОВНИЙ РУШІЙ ---
    { 
        id: 'eng_ultimate', name: 'Гіпер-Турбіна', tier: 'IV', desc: 'Найкраща турбіна. Дозволяє досягти другої космічної швидкості.', 
        x: 1300, y: 1400, // Вгору
        req: 'eng_start', owned: false, img: 'images/Turbina.png',
        cost: { iron: 350, fuel: 500, coins: 900 }
    },

    // --- ГІЛКА Б: МАНЕВРОВІСТЬ ---
    { 
        id: 'eng_side', name: 'Бокові Рушії', tier: 'II', desc: 'Покращення всіх маневрових двигунів для стабілізації.', 
        x: 1300, y: 1600, // Вниз
        req: 'eng_start', owned: false, img: 'images/Turbina.png',
        cost: { iron: 300, fuel: 250, coins: 400 }
    },


    // =======================================================
    // === ГРУПА 3: НІС (Сенсори) ===
    // Послідовність: Ніс -> Новий покращений ніс
    // =======================================================

    // 1. Старт (Ніс)
    { 
        id: 'nose_start', name: 'Титановий Конус', tier: 'I', desc: 'Посилений захист від тертя атмосфери.', 
        x: 1000, y: 1850, 
        req: null, owned: true, img: 'images/Nose.png',
        cost: { iron: 0, fuel: 0, coins: 0 }
    },
    // 2. Фінал носа
    { 
        id: 'nose_adv', name: 'Аеро-Композит', tier: 'III', desc: 'Новий покращений ніс з вбудованими сенсорами дальньої дії.', 
        x: 1300, y: 1850, // Пряма лінія
        req: 'nose_start', owned: false, img: 'images/Nose.png',
        cost: { iron: 250, fuel: 200, coins: 550 }
    }
];

async function syncWithSave() {
    try {
        const res = await fetch(`/api/get_upgrades?family_id=${window.userFamilyId}`);
        const unlocked = await res.json();
        treeNodes.forEach(node => { if (unlocked.includes(node.id)) node.owned = true; });
    } catch (e) { console.error("Sync error:", e); }
}

async function buyUpgrade() {
    if (!selectedNode || selectedNode.owned) return;
    const res = await fetch('/api/upgrade', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ family_id: window.userFamilyId, module_id: selectedNode.id, cost: selectedNode.cost, req: selectedNode.req })
    });
    const result = await res.json();
    if (result.success) {
        selectedNode.owned = true;
        init(); 
        alert(result.message);
    } else { alert("Помилка: " + result.error); }
}

function init() {
    syncWithSave().then(() => {
        canvas.innerHTML = ''; 
        canvas.style.transformOrigin = '0 0';
        treeNodes.forEach(node => {
            const div = document.createElement('div');
            div.className = 'node' + (node.owned ? ' owned' : '');
            div.id = `node-${node.id}`;
            div.style.left = node.x + 'px';
            div.style.top = node.y + 'px';
            div.innerHTML = `
                <div class="node-img-box"><img src="${node.img}" class="node-icon"></div>
                <div class="node-tier">TIER ${node.tier}</div>
                <div class="node-title">${node.name}</div>
                <div class="node-status">${node.owned ? '✔' : ''}</div>`;
            div.onclick = (e) => { e.stopPropagation(); highlightPath(node.id); openPanel(node); };
            canvas.appendChild(div);
            if (node.req) drawLine(node);
        });
        centerViewport();
        const researchBtn = document.querySelector('.action-btn');
        if(researchBtn) researchBtn.onclick = buyUpgrade;
    });
}

function openPanel(node) {
    selectedNode = node;
    document.getElementById('node-name').innerText = node.name;
    document.getElementById('node-tier').innerText = `TIER ${node.tier}`;
    document.getElementById('node-desc').innerText = node.desc;
    document.getElementById('node-image').src = node.img;

    const costDiv = document.getElementById('node-cost');
    if (node.owned) {
        costDiv.innerHTML = '<div class="cost-owned-msg">ВЖЕ ВСТАНОВЛЕНО</div>';
    } else {
        const c = node.cost;
        costDiv.innerHTML = `
            <div class="cost-cell"><span class="cost-icon">☁️</span><span class="cost-value">${c.iron}</span></div>
            <div class="cost-cell"><span class="cost-icon">🎈</span><span class="cost-value">${c.fuel}</span></div>
            <div class="cost-cell"><span class="cost-icon">🪙</span><span class="cost-value">${c.coins}</span></div>`;
    }

    const btn = document.querySelector('.action-btn');
    if (node.owned) {
        btn.textContent = 'В АНГАРІ'; btn.classList.add('disabled'); btn.disabled = true;
    } else {
        let parent = treeNodes.find(n => n.id === node.req);
        if (parent && !parent.owned) {
            btn.textContent = 'НЕМАЄ ДОСТУПУ'; btn.classList.add('disabled'); btn.disabled = true;
        } else {
            btn.textContent = 'ДОСЛІДИТИ'; btn.classList.remove('disabled'); btn.disabled = false;
        }
    }
    document.getElementById('info-panel').classList.add('active');
}

function drawLine(node) {
    const parent = treeNodes.find(n => n.id === node.req);
    if (!parent) return;
    const line = document.createElement('div');
    line.className = 'line';
    const startX = parent.x + NODE_WIDTH;
    const startY = parent.y + NODE_HEIGHT / 2;
    const endX = node.x;
    const endY = node.y + NODE_HEIGHT / 2;
    const dist = Math.sqrt(Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2));
    line.style.width = dist + 'px';
    line.style.left = startX + 'px';
    line.style.top = startY + 'px';
    line.style.transform = `rotate(${Math.atan2(endY - startY, endX - startX)}rad)`;
    canvas.appendChild(line);
}

function highlightPath(nodeId) {
    document.querySelectorAll('.node, .line').forEach(el => el.classList.remove('highlight'));
    let curr = nodeId;
    while (curr) {
        document.getElementById(`node-${curr}`)?.classList.add('highlight');
        curr = treeNodes.find(n => n.id === curr)?.req;
    }
}

function centerViewport() {
    currentX = window.innerWidth / 2 - 1300;
    currentY = window.innerHeight / 2 - 1500;
    updateCanvasPosition();
}

function updateCanvasPosition() {
    canvas.style.transform = `translate(${currentX}px, ${currentY}px) scale(${scale})`;
}

viewport.addEventListener('mousedown', (e) => {
    if (e.target.closest('.node')) return;
    isDragging = true;
    startX = e.clientX - currentX;
    startY = e.clientY - currentY;
});

window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    currentX = e.clientX - startX;
    currentY = e.clientY - startY;
    updateCanvasPosition();
});

window.addEventListener('mouseup', () => isDragging = false);

window.onload = init;