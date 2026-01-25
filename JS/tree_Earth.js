const canvas = document.getElementById('canvas');
const viewport = document.getElementById('viewport');

// Змінні для позиції
let currentX = 0; 
let currentY = 0; 
let isDragging = false;
let startX, startY;
const NODE_WIDTH = 210;  // Було 150, стало 210 (ширина ноди)
const NODE_HEIGHT = 85;
// --- 1. ОНОВЛЕНІ КООРДИНАТИ (Рівні лінії) ---
// Базова точка X=1000, Y=1000. Крок по X = 250px, Крок по Y = 200px
const treeNodes = [
    // --- РЯДОК 1: Конус-верхівка ---
    { 
        id: 'gu1', name: 'Конус-верхівка', tier: 'I', desc: 'Аеродинамічний обтікач для зниження опору повітря під час зльоту.', 
        x: 1000, y: 1000, 
        req: null, owned: true, img: 'images/modules/nose.png' 
    },
    { 
        id: 'gu2', name: 'Сенсорний шпиль', tier: 'II', desc: 'Модернізована верхівка з датчиками атмосфери та телеметрією.', 
        x: 1400, y: 1000,
        req: 'gu1', owned: false, img: 'images/modules/ai.png' 
    },

    // --- РЯДОК 2: Корпус ---
    { 
        id: 'nc1', name: 'Корпус', tier: 'I', desc: 'Стандартна алюмінієва оболонка для паливних баків.', 
        x: 1000, y: 1250,
        req: null, owned: true, img: 'images/modules/body.png' 
    },
    { 
        id: 'h1', name: 'Титановий каркас', tier: 'II', desc: 'Посилена конструкція, що витримує перевантаження до 15G.', 
        x: 1400, y: 1250,
        req: 'nc1', owned: false, img: 'images/modules/fairing.png' 
    },

    // --- РЯДОК 3: Турбіна ---
    { 
        id: 'e1', name: 'Турбіна', tier: 'I', desc: 'Базовий насос для подачі паливної суміші в камеру згоряння.', 
        x: 1000, y: 1500, 
        req: null, owned: true, img: 'images/Turbina.png' 
    },
    { 
        id: 'e2', name: 'Турбо-нагнітач', tier: 'II', desc: 'Подвійна система нагнітання для максимальної тяги двигуна.', 
        x: 1400, y: 1500, 
        req: 'e1', owned: false, img: 'images/Turbina.png' 
    },

    // --- РЯДОК 4: Надкрилки ---
    {
        id: 'a1', name: 'Надкрилки', tier: 'I', desc: 'Пасивні стабілізатори для стійкості ракети в польоті.',
        x: 1000, y: 1750,
        req: null, owned: true, img: 'images/Stabilizator.png'
    },
    {
        id: 'a2', name: 'Активні закрилки', tier: 'II', desc: 'Рухомі елементи крил для точного маневрування при посадці.',
        x: 1400, y: 1750,
        req: 'a1', owned: false, img: 'images/Stabilizator.png'
    }
];

// --- DRAG LOGIC ---
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

// --- INIT ---
function init() {
    // 1. Малюємо ноди
    treeNodes.forEach(node => {
        const div = document.createElement('div');
        div.className = 'node';
        if (node.owned) div.classList.add('owned');
        div.id = `node-${node.id}`;
        
        // Позиціонування
        div.style.left = node.x + 'px';
        div.style.top = node.y + 'px';

        const imageSrc = node.img ? node.img : 'images/placeholder_icon.png';
        const checkmarkHTML = node.owned ? '<span class="checkmark">✔</span>' : '';

        div.innerHTML = `
            <div class="node-text-col">
                <div class="node-tier">TIER ${node.tier}</div>
                <div class="node-title">${node.name}</div>
            </div>
            <div class="node-img-box">
                <img src="${imageSrc}" class="node-icon" onerror="this.style.opacity=0">
                <div class="node-status">${checkmarkHTML}</div>
            </div>
            `;
        
        div.onclick = (e) => {
            e.stopPropagation();
            highlightPath(node.id);
            openPanel(node);
        };
        canvas.appendChild(div);

        if (node.req) drawLine(node);
    });

    // 2. Центруємо екран на дереві
    centerViewport();
}

// --- ФУНКЦІЯ ЦЕНТРУВАННЯ ---
function centerViewport() {
    // Знаходимо приблизний центр нашого дерева
    // По X: від 1000 до 1500 -> центр 1250
    // По Y: від 1000 до 1400 -> центр 1200
    const treeCenterX = 1250; 
    const treeCenterY = 1200;

    // Центр екрану користувача
    const screenCenterX = window.innerWidth / 2;
    const screenCenterY = window.innerHeight / 2;

    // Зсув = Центр Екрану - Центр Дерева
    currentX = screenCenterX - treeCenterX;
    currentY = screenCenterY - treeCenterY;

    // Застосовуємо
    updateCanvasPosition();
}

function drawLine(node) {
    const parent = treeNodes.find(n => n.id === node.req);
    if (!parent) return;

    const line = document.createElement('div');
    line.className = 'line';
    line.id = `line-${node.id}`;

    // Координати:
    // Початок (x1, y1): Правий край батьківського елемента, по центру висоти
    const startX = parent.x + NODE_WIDTH; 
    const startY = parent.y + (NODE_HEIGHT / 2);

    // Кінець (x2, y2): Лівий край дочірнього елемента, по центру висоти
    const endX = node.x;
    const endY = node.y + (NODE_HEIGHT / 2);

    // Математика довжини та кута
    const dx = endX - startX;
    const dy = endY - startY;
    const dist = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx) * (180 / Math.PI); // Переводимо в градуси

    // Стилі лінії
    line.style.width = dist + 'px';
    line.style.left = startX + 'px';
    line.style.top = startY + 'px';
    
    // Важливо: transform-origin має бути '0 50%' (лівий край, центр по вертикалі)
    line.style.transformOrigin = '0 50%'; 
    line.style.transform = `rotate(${angle}deg)`;

    canvas.appendChild(line);
}

// Функції панелі (залишаємо як було)
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
    document.getElementById('node-name').innerText = node.name;
    document.getElementById('node-tier').innerText = `TIER ${node.tier}`;
    document.getElementById('node-desc').innerText = node.desc;

    // 🖼 Картинка модуля
    const img = document.getElementById('node-image');
    img.src = node.img || 'images/modules/placeholder.png';

    // 🔘 Кнопка дослідження
    const btn = document.querySelector('.action-btn');

    if (node.owned) {
        btn.textContent = 'ДОСЛІДЖЕНО';
        btn.classList.add('disabled');
        btn.disabled = true;
    } else {
        btn.textContent = 'ДОСЛІДИТИ';
        btn.classList.remove('disabled');
        btn.disabled = false;
    }

    document.getElementById('info-panel').classList.add('active');
}

function closePanel() {
    document.getElementById('info-panel').classList.remove('active');
    document.querySelectorAll('.node, .line').forEach(el => el.classList.remove('highlight'));
}

window.onload = init;