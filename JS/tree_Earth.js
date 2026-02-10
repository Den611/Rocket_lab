// Отримання canvas та viewport для рендеру та переміщення камери
const canvas = document.getElementById('canvas');
const viewport = document.getElementById('viewport');

// Ініціалізація Family ID з URL (першочергово)
const urlParams = new URLSearchParams(window.location.search);
window.userFamilyId = urlParams.get('family_id');

// Налаштування камери та зуму
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

// Дерево технологій Землі
window.treeNodes = [
    {
        id: 'gu1',
        name: 'Конус-верхівка',
        tier: 'I',
        desc: 'Аеродинамічний обтікач для зниження опору повітря під час зльоту.',
        x: 1000, y: 1000,
        req: null, owned: true, img: 'images/Nose.png',
        rocketKey: 'nose', level: 1,
        cost: { iron: 0, fuel: 0, coins: 0 }
    },
    {
        id: 'gu2',
        name: 'Сенсорний шпиль',
        tier: 'II',
        desc: 'Модернізована верхівка з датчиками атмосфери та телеметрією.',
        x: 1400, y: 1000,
        req: 'gu1', owned: false, img: 'images/Nose.png',
        rocketKey: 'nose', level: 2,
        cost: { iron: 500, fuel: 100, coins: 250 }
    },
    {
        id: 'nc1',
        name: 'Корпус',
        tier: 'I',
        desc: 'Стандартна алюмінієва оболонка для паливних баків.',
        x: 1000, y: 1250,
        req: null, owned: true, img: 'images/Korpus.png',
        rocketKey: 'body', level: 1,
        cost: { iron: 0, fuel: 0, coins: 0 }
    },
    {
        id: 'h1',
        name: 'Сталевий Корпус',
        tier: 'II',
        desc: 'Базова основа ракети. Витримує більші навантаження.',
        x: 1400, y: 1250,
        req: 'nc1', owned: false, img: 'images/Korpus.png',
        rocketKey: 'body', level: 2,
        cost: { iron: 800, fuel: 50, coins: 400 }
    },
    {
        id: 'e1',
        name: 'Турбіна',
        tier: 'I',
        desc: 'Базовий насос для подачі паливної суміші в камеру згоряння.',
        x: 1000, y: 1500,
        req: null, owned: true, img: 'images/Turbina.png',
        rocketKey: 'engine', level: 1,
        cost: { iron: 0, fuel: 0, coins: 0 }
    },
    {
        id: 'e2',
        name: 'Турбо-нагнітач',
        tier: 'II',
        desc: 'Подвійна система нагнітання для максимальної тяги двигуна.',
        x: 1400, y: 1500,
        req: 'e1', owned: false, img: 'images/Turbina.png',
        rocketKey: 'engine', level: 2,
        cost: { iron: 400, fuel: 300, coins: 600 }
    },
    {
        id: 'a1',
        name: 'Надкрилки',
        tier: 'I',
        desc: 'Пасивні стабілізатори для стійкості ракети в польоті.',
        x: 1000, y: 1750,
        req: null, owned: true, img: 'images/Stabilizator.png',
        rocketKey: 'fins', level: 1,
        cost: { iron: 0, fuel: 0, coins: 0 }
    },
    {
        id: 'a2',
        name: 'Активні закрилки',
        tier: 'II',
        desc: 'Рухомі елементи крил для точного маневрування при посадці.',
        x: 1400, y: 1750,
        req: 'a1', owned: false, img: 'images/Stabilizator.png',
        rocketKey: 'fins', level: 2,
        cost: { iron: 300, fuel: 150, coins: 350 }
    }
];

// Синхронізація куплених модулів з базою даних
async function syncWithSave() {
    const familyId = window.userFamilyId || (typeof GLOBAL_FAMILY_ID !== 'undefined' ? GLOBAL_FAMILY_ID : null);
    if (!familyId) return;

    try {
        const res = await fetch(`/api/get_upgrades?family_id=${familyId}`);
        const unlocked = await res.json();
        treeNodes.forEach(node => { 
            if (unlocked.includes(node.id)) node.owned = true; 
        });
    } catch (e) { 
        console.error("Sync error:", e); 
    }
}

// Купівля (дослідження) нового модуля
async function buyUpgrade() {
    if (!selectedNode || selectedNode.owned) return;
    
    const familyId = window.userFamilyId || (typeof GLOBAL_FAMILY_ID !== 'undefined' ? GLOBAL_FAMILY_ID : null);
    
    if (!familyId) {
        alert("Помилка: Не знайдено ID сім'ї.");
        return;
    }

    try {
        const res = await fetch('/api/upgrade', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                family_id: familyId, 
                module_id: selectedNode.id, 
                cost: selectedNode.cost, 
                req: selectedNode.req 
            })
        });
        const result = await res.json();
        if (result.success) {
            selectedNode.owned = true;
            init(); // Оновлюємо візуальне дерево
            alert(result.message);
        } else { 
            alert("Помилка: " + result.error); 
        }
    } catch (e) {
        console.error("Buy error:", e);
    }
}

// Побудова дерева та запуск логіки
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
            div.onclick = (e) => { 
                e.stopPropagation(); 
                highlightPath(node.id); 
                openPanel(node); 
            };
            canvas.appendChild(div);
            if (node.req) drawLine(node);
        });
        centerViewport();
        const researchBtn = document.querySelector('.action-btn');
        if(researchBtn) researchBtn.onclick = buyUpgrade;
    });
}

// Відкриття панелі інформації про модуль
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
            <div class="cost-cell"><span class="cost-icon">🔩</span><span class="cost-value">${c.iron}</span></div>
            <div class="cost-cell"><span class="cost-icon">💠</span><span class="cost-value">${c.fuel}</span></div>
            <div class="cost-cell"><span class="cost-icon">🪙</span><span class="cost-value">${c.coins}</span></div>`;
    }

    const btn = document.querySelector('.action-btn');
    if (node.owned) {
        btn.textContent = 'В АНГАРІ'; 
        btn.classList.add('disabled'); 
        btn.disabled = true;
    } else {
        let parent = treeNodes.find(n => n.id === node.req);
        if (parent && !parent.owned) {
            btn.textContent = 'НЕМАЄ ДОСТУПУ'; 
            btn.classList.add('disabled'); 
            btn.disabled = true;
        } else {
            btn.textContent = 'ДОСЛІДИТИ'; 
            btn.classList.remove('disabled'); 
            btn.disabled = false;
        }
    }
    document.getElementById('info-panel').classList.add('active');
}

// Малювання ліній зв'язку між вузлами
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

// Підсвічування шляху до кореня
function highlightPath(nodeId) {
    document.querySelectorAll('.node, .line').forEach(el => el.classList.remove('highlight'));
    let curr = nodeId;
    while (curr) {
        document.getElementById(`node-${curr}`)?.classList.add('highlight');
        curr = treeNodes.find(n => n.id === curr)?.req;
    }
}

// Управління камерою та відображенням
function centerViewport() {
    currentX = window.innerWidth / 2 - 1300;
    currentY = window.innerHeight / 2 - 1500;
    updateCanvasPosition();
}

function updateCanvasPosition() {
    canvas.style.transform = `translate(${currentX}px, ${currentY}px) scale(${scale})`;
}

// Логіка перетягування (Drag-and-Drop)
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

// Глобальна функція закриття панелі (може викликатися з HTML)
window.closePanel = function() {
    document.getElementById('info-panel').classList.remove('active');
};

// Отримання та відображення ресурсів з API
async function updateResources() {
    const familyId = window.userFamilyId || (typeof GLOBAL_FAMILY_ID !== 'undefined' ? GLOBAL_FAMILY_ID : null);
    
    if (!familyId) {
        console.warn("UpdateResources: family_id не знайдено");
        return;
    }

    try {
        const res = await fetch(`/api/inventory?family_id=${familyId}`);
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        
        const data = await res.json();
        
        if (data.resources) {
            const ironEl = document.getElementById('val-iron');
            const fuelEl = document.getElementById('val-fuel');
            const coinsEl = document.getElementById('val-coins');

            if (ironEl) ironEl.innerText = data.resources.iron;
            if (fuelEl) fuelEl.innerText = data.resources.fuel;
            if (coinsEl) coinsEl.innerText = data.resources.coins;
        }
    } catch (e) {
        console.error("Помилка завантаження ресурсів:", e);
    }
}

// Таймер оновлення ресурсів (кожні 10 сек)
updateResources();
setInterval(updateResources, 10000);

window.addEventListener('mouseup', () => isDragging = false);

// Запуск ініціалізації при повному завантаженні вікна
window.onload = init;