const canvas = document.getElementById('canvas');
const viewport = document.getElementById('viewport');

// Змінні для позиції
let currentX = 0; 
let currentY = 0; 
let isDragging = false;
let startX, startY;
const NODE_WIDTH = 150;
const NODE_HEIGHT = 145;

// Змінна для збереження вибраного модуля (щоб знати, що купувати)
let selectedNode = null;

// --- 1. ОНОВЛЕНІ ДАНІ (Додано rocketKey та level) ---
// rocketKey має співпадати з ключами в index.html (nose, body, engine, fins)
const treeNodes = [
    // --- КАТЕГОРІЯ 1: НІС (NOSE) ---
    {
        id: 'gu1',
        name: 'Конус-верхівка',
        tier: 'I',
        desc: 'Аеродинамічний обтікач для зниження опору повітря під час зльоту.',
        x: 1000, y: 1000,
        req: null, owned: true, img: 'images/Nose.png',
        rocketKey: 'nose', level: 1 // --- НОВЕ: Зв'язок з головним файлом
    },
    {
        id: 'gu2',
        name: 'Сенсорний шпиль',
        tier: 'II',
        desc: 'Модернізована верхівка з датчиками атмосфери та телеметрією.',
        x: 1400, y: 1000,
        req: 'gu1', owned: false, img: 'images/Nose.png',
        rocketKey: 'nose', level: 2
    },

    // --- КАТЕГОРІЯ 2: КОРПУС (BODY) ---
    {
        id: 'nc1',
        name: 'Корпус',
        tier: 'I',
        desc: 'Стандартна алюмінієва оболонка для паливних баків.',
        x: 1000, y: 1250,
        req: null, owned: true, img: 'images/Korpus.png',
        rocketKey: 'body', level: 1
    },
    {
        id: 'h1',
        name: 'Сталевий Корпус',
        tier: 'II',
        desc: 'Базова основа ракети.',
        x: 1400, y: 1250,
        req: 'nc1', owned: false, img: 'images/Korpus.png',
        rocketKey: 'body', level: 2
    },

    // --- КАТЕГОРІЯ 3: ДВИГУН (ENGINE) ---
    {
        id: 'e1',
        name: 'Турбіна',
        tier: 'I',
        desc: 'Базовий насос для подачі паливної суміші в камеру згоряння.',
        x: 1000, y: 1500,
        req: null, owned: true, img: 'images/Turbina.png',
        rocketKey: 'engine', level: 1
    },
    {
        id: 'e2',
        name: 'Турбо-нагнітач',
        tier: 'II',
        desc: 'Подвійна система нагнітання для максимальної тяги двигуна.',
        x: 1400, y: 1500,
        req: 'e1', owned: false, img: 'images/Turbina.png',
        rocketKey: 'engine', level: 2
    },

    // --- КАТЕГОРІЯ 4: КРИЛА (FINS) ---
    {
        id: 'a1',
        name: 'Надкрилки',
        tier: 'I',
        desc: 'Пасивні стабілізатори для стійкості ракети в польоті.',
        x: 1000, y: 1750,
        req: null, owned: true, img: 'images/Stabilizator.png',
        rocketKey: 'fins', level: 1
    },
    {
        id: 'a2',
        name: 'Активні закрилки',
        tier: 'II',
        desc: 'Рухомі елементи крил для точного маневрування при посадці.',
        x: 1400, y: 1750,
        req: 'a1', owned: false, img: 'images/Stabilizator.png',
        rocketKey: 'fins', level: 2
    }
];

// --- DRAG LOGIC (Без змін) ---
viewport.addEventListener('mousedown', (e) => {
    if (e.target.closest('.node')) return;
    isDragging = true;
    startX = e.clientX - currentX;
    startY = e.clientY - currentY;
    viewport.style.cursor = 'grabbing';
});

window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    e.preventDefault();
    currentX = e.clientX - startX;
    currentY = e.clientY - startY;
    updateCanvasPosition();
});

window.addEventListener('mouseup', () => {
    isDragging = false;
    viewport.style.cursor = 'grab';
});

function updateCanvasPosition() {
    canvas.style.transform = `translate(${currentX}px, ${currentY}px)`;
}

// --- СИНХРОНІЗАЦІЯ З ПАМ'ЯТТЮ (НОВЕ) ---
function syncWithSave() {
    // 1. Беремо сейв
    const savedData = localStorage.getItem('myRocketSave');
    if (!savedData) return; // Якщо сейву нема, все лишається як є (false)

    const rocketState = JSON.parse(savedData);

    // 2. Проходимо по дереву і ставимо owned = true, якщо рівень дозволяє
    treeNodes.forEach(node => {
        // Наприклад: якщо у сейві nose: 2, то і nose level 1, і nose level 2 стануть owned
        if (rocketState[node.rocketKey] >= node.level) {
            node.owned = true;
        }
    });
}

// --- INIT ---
function init() {
    // Спочатку оновлюємо дані з пам'яті
    syncWithSave();

    // 1. Малюємо ноди
    treeNodes.forEach(node => {
        const div = document.createElement('div');
        div.className = 'node';
        if (node.owned) div.classList.add('owned');
        div.id = `node-${node.id}`;
        
        // Позиціонування
        div.style.left = node.x + 'px';
        div.style.top = node.y + 'px';

        const checkmarkHTML = node.owned ? '<span class="checkmark">✔</span>' : '';
        const imageSrc = node.img ? node.img : 'images/placeholder_icon.png';

        div.innerHTML = `
            <div class="node-img-box">
                <img src="${imageSrc}" class="node-icon" onerror="this.style.opacity=0">
            </div>
            <div class="node-tier">TIER ${node.tier}</div>
            <div class="node-title">${node.name}</div>
            <div class="node-status">${checkmarkHTML}</div>
        `;
        
        div.onclick = (e) => {
            e.stopPropagation();
            highlightPath(node.id);
            openPanel(node);
        };
        canvas.appendChild(div);

        if (node.req) drawLine(node);
    });

    // 2. Центруємо екран
    centerViewport();

    // 3. --- НОВЕ: Додаємо слухач на кнопку в панелі ---
    const researchBtn = document.querySelector('.action-btn');
    if(researchBtn) {
        researchBtn.addEventListener('click', buyUpgrade);
    }
}

// --- ЛОГІКА ПОКУПКИ (НОВЕ) ---
function buyUpgrade() {
    if (!selectedNode) return;
    if (selectedNode.owned) return; 

    // Тут можна додати: if (money < cost) return;

    // 1. Оновлюємо локальний стан ноди (візуально)
    selectedNode.owned = true;

    // 2. Оновлюємо глобальний сейв (localStorage)
    let currentSave = localStorage.getItem('myRocketSave');
    
    // Якщо сейву нема - створюємо його з ПРАВИЛЬНИМИ стартовими даними
    if (!currentSave) {
        currentSave = { 
            nose: 1, body: 1, engine: 1, fins: 1, // Стартовий набір
            cabin: 0, cargo: 0, solar: 0, booster: 0 
        };
    } else {
        currentSave = JSON.parse(currentSave);
    }

    // Записуємо новий рівень
    if (currentSave[selectedNode.rocketKey] < selectedNode.level) {
        currentSave[selectedNode.rocketKey] = selectedNode.level;
    }

    localStorage.setItem('myRocketSave', JSON.stringify(currentSave));

    // 3. Візуальні оновлення
    const nodeDiv = document.getElementById(`node-${selectedNode.id}`);
    if (nodeDiv) {
        nodeDiv.classList.add('owned');
        nodeDiv.querySelector('.node-status').innerHTML = '<span class="checkmark">✔</span>';
    }

    const btn = document.querySelector('.action-btn');
    btn.textContent = 'ДОСЛІДЖЕНО';
    btn.classList.add('disabled');
    btn.disabled = true;

    // Якщо це TIER 2, можна додати лінію з'єднання як активну
    if (selectedNode.req) {
         const line = document.getElementById(`line-${selectedNode.id}`);
         if(line) line.style.opacity = '1'; // або додати клас active
    }

    alert(`Успішно досліджено: ${selectedNode.name}!`);
}


function centerViewport() {
    const treeCenterX = 1300; 
    const treeCenterY = 1500;
    const screenCenterX = window.innerWidth / 2;
    const screenCenterY = window.innerHeight / 2;
    currentX = screenCenterX - treeCenterX;
    currentY = screenCenterY - treeCenterY;
    updateCanvasPosition();
}

function drawLine(node) {
    const parent = treeNodes.find(n => n.id === node.req);
    if (!parent) return;

    const line = document.createElement('div');
    line.className = 'line';
    line.id = `line-${node.id}`;

    // Перевіряємо, чи батько куплений, щоб підсвітити лінію (опціонально)
    if (parent.owned && node.owned) {
        // line.classList.add('active-line'); // Можна додати в CSS стиль для active-line
    }

    const startX = parent.x + NODE_WIDTH;
    const startY = parent.y + NODE_HEIGHT / 2;
    const endX = node.x;
    const endY = node.y + NODE_HEIGHT / 2;
    const dx = endX - startX;
    const dy = endY - startY;
    const dist = Math.sqrt(dx * dx + dy * dy);

    line.style.width = dist + 'px';
    line.style.left = startX + 'px';
    line.style.top = startY + 'px';
    line.style.transform = `rotate(${Math.atan2(dy, dx)}rad)`;

    canvas.appendChild(line);
}

function highlightPath(nodeId) {
    document.querySelectorAll('.node, .line').forEach(el => el.classList.remove('highlight'));
    let currentId = nodeId;
    while (currentId) {
        document.getElementById(`node-${currentId}`)?.classList.add('highlight');
        document.getElementById(`line-${currentId}`)?.classList.add('highlight');
        const node = treeNodes.find(n => n.id === currentId);
        currentId = node ? node.req : null;
    }
}

function openPanel(node) {
    selectedNode = node; // Запам'ятовуємо, що зараз відкрито

    document.getElementById('node-name').innerText = node.name;
    document.getElementById('node-tier').innerText = `TIER ${node.tier}`;
    document.getElementById('node-desc').innerText = node.desc;
    const img = document.getElementById('node-image');
    img.src = node.img || 'images/modules/placeholder.png';

    const btn = document.querySelector('.action-btn');

    // Перевірка: чи куплений ЦЕЙ модуль
    if (node.owned) {
        btn.textContent = 'ДОСЛІДЖЕНО';
        btn.classList.add('disabled');
        btn.disabled = true;
    } else {
        // Перевірка: чи куплений ПОПЕРЕДНІЙ модуль (батьківський)
        // Якщо це Tier 2, а Tier 1 ще не куплено - блокуємо кнопку
        let parent = treeNodes.find(n => n.id === node.req);
        if (parent && !parent.owned) {
            btn.textContent = 'ЗАБЛОКОВАНО';
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

function closePanel() {
    document.getElementById('info-panel').classList.remove('active');
    document.querySelectorAll('.node, .line').forEach(el => el.classList.remove('highlight'));
    selectedNode = null;
}

window.onload = init;