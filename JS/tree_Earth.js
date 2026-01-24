const canvas = document.getElementById('canvas');
const viewport = document.getElementById('viewport');

// Змінні для позиції
let currentX = 0; 
let currentY = 0; 
let isDragging = false;
let startX, startY;
const NODE_WIDTH = 150;
const NODE_HEIGHT = 145;
// --- 1. ОНОВЛЕНІ КООРДИНАТИ (Рівні лінії) ---
// Базова точка X=1000, Y=1000. Крок по X = 250px, Крок по Y = 200px
const treeNodes = [
    // --- РЯДОК 1: Керування ---
    { 
        id: 'gu1', name: 'Heavy-X Control', tier: 'I', desc: 'Блок керування.', 
        x: 1000, y: 1000, 
        req: null, owned: true, img: 'images/modules/nose.png' 
    },
    { 
        id: 'gu2', name: 'AI Neuro-Pilot', tier: 'II', desc: 'Авто-пілот.', 
        x: 1250, y: 1000, // Прямо праворуч
        req: 'gu1', owned: false, img: 'images/modules/ai.png' 
    },

    // --- РЯДОК 2: Корпус і захист ---
    { 
        id: 'nc1', name: 'Payload Shell', tier: 'I', desc: 'Обтікач.', 
        x: 1000, y: 1200, 
        req: null, owned: true, img: 'images/modules/fairing.png' 
    },
    { 
        id: 'h1', name: 'Heavy-X Frame', tier: 'II', desc: 'Титановий корпус.', 
        x: 1250, y: 1200, // Прямо праворуч
        req: 'nc1', owned: false, img: 'images/modules/body.png' 
    },

    // --- РЯДОК 3: Двигуни ---
    { 
        id: 'e1', name: 'Chemical Engine', tier: 'I', desc: 'Двигун.', 
        x: 1000, y: 1400, 
        req: null, owned: true, img: 'images/modules/engine.png' 
    },
    { 
        id: 'e2', name: 'Dual Boosters', tier: 'II', desc: 'Прискорювачі.', 
        x: 1250, y: 1400, // Прямо праворуч
        req: 'e1', owned: false, img: 'images/modules/booster.png' 
    },

    {
        id: 'a1',
        name: 'Thermal Shielding',
        tier: 'I',
        desc: 'Захист від перегріву.',
        x: 1000,
        y: 1600,
        req: null,
        owned: true,
        img: 'images/modules/shield.png'
    },
    {
        id: 'a2',
        name: 'Quantum Telemetry',
        tier: 'II',
        desc: 'Розширена телеметрія.',
        x: 1250,
        y: 1600,
        req: 'a1',
        owned: false,
        img: 'images/modules/quantum.png'
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

    // 🔹 START — права сторона батька
    const startX = parent.x + NODE_WIDTH;
    const startY = parent.y + NODE_HEIGHT / 2;

    // 🔹 END — ліва сторона дитини
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