const canvas = document.getElementById('canvas');
const viewport = document.getElementById('viewport');

// Змінні для позиції
let currentX = 0; 
let currentY = 0; 
let isDragging = false;
let startX, startY;
const NODE_WIDTH = 150;
const NODE_HEIGHT = 145;

const treeNodes = [
    // === ГРУПА 1: ВЕРХНЯ (2 в ряд -> розвилка -> верх продовжується) ===
    { 
        id: 'g1_1', name: 'Core Module', tier: 'I', desc: 'Центральний модуль.', 
        x: 1000, y: 1000, 
        req: null, owned: true, img: 'images/modules/nose.png' 
    },
    { 
        id: 'g1_2', name: 'Processing Unit', tier: 'II', desc: 'Обробка даних.', 
        x: 1250, y: 1000, // Другий у лінії
        req: 'g1_1', owned: false, img: 'images/modules/ai.png' 
    },
    // Розвилка починається після другого блоку (g1_2)
    { 
        id: 'g1_up', name: 'Adv. Logic', tier: 'III', desc: 'Вища логіка.', 
        x: 1500, y: 900, // Вгору
        req: 'g1_2', owned: false, img: 'images/modules/quantum.png' 
    },
    { 
        id: 'g1_down', name: 'Firewall', tier: 'III', desc: 'Захист.', 
        x: 1500, y: 1100, // Вниз
        req: 'g1_2', owned: false, img: 'images/modules/shield.png' 
    },
    // Продовження верхньої гілки
    { 
        id: 'g1_end', name: 'AI Nexus', tier: 'IV', desc: 'Ядро ШІ.', 
        x: 1750, y: 900, // Прямо від верхнього
        req: 'g1_up', owned: false, img: 'images/modules/ai.png' 
    },


    // === ГРУПА 2: СЕРЕДНЯ (1 -> розвилка) ===
    { 
        id: 'g2_1', name: 'Engines', tier: 'I', desc: 'Двигуни.', 
        x: 1000, y: 1400, // Відступ вниз
        req: null, owned: true, img: 'images/modules/engine.png' 
    },
    { 
        id: 'g2_up', name: 'Ion Thruster', tier: 'II', desc: 'Іонний привід.', 
        x: 1250, y: 1300, // Вгору
        req: 'g2_1', owned: false, img: 'images/modules/booster.png' 
    },
    { 
        id: 'g2_down', name: 'Warp Drive', tier: 'II', desc: 'Варп-двигун.', 
        x: 1250, y: 1500, // Вниз
        req: 'g2_1', owned: false, img: 'images/modules/quantum.png' 
    },


    // === ГРУПА 3: НИЖНЯ (Дві паралельні лінії) ===
    // Лінія 1
    { 
        id: 'g3_a1', name: 'Life Support', tier: 'I', desc: 'Життєзабезпечення.', 
        x: 1000, y: 1700, 
        req: null, owned: true, img: 'images/modules/fairing.png' 
    },
    { 
        id: 'g3_a2', name: 'Cryo Pods', tier: 'II', desc: 'Кріо-капсули.', 
        x: 1250, y: 1700, // Прямо
        req: 'g3_a1', owned: false, img: 'images/modules/body.png' 
    },

    // Лінія 2
    { 
        id: 'g3_b1', name: 'Cargo Bay', tier: 'I', desc: 'Вантажний відсік.', 
        x: 1000, y: 1900, 
        req: null, owned: true, img: 'images/modules/body.png' 
    },
    { 
        id: 'g3_b2', name: 'Expansion', tier: 'II', desc: 'Розширення.', 
        x: 1250, y: 1900, // Прямо
        req: 'g3_b1', owned: false, img: 'images/modules/shield.png' 
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
    // Центр схеми
    // X: середина між 1000 і 1750 ~ 1375
    // Y: середина між 1000 і 1900 ~ 1450
    const treeCenterX = 1375; 
    const treeCenterY = 1450;

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