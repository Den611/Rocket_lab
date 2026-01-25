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
    // === ГРУПА 1: Корпус (Основа -> Відсік/Панелі або Надкрилки) ===
    // Корінь групи
    { 
        id: 'root1', name: 'Сталевий Корпус', tier: 'I', desc: 'Базова основа ракети.', 
        x: 1000, y: 1100, 
        req: null, owned: true, img: 'images/Korpus.png' 
    },
    // Верхня гілка (Додатковий відділ -> Сонячні панелі)
    { 
        id: 'branch1_up1', name: 'Вантажний Відсік', tier: 'II', desc: 'Додатковий модуль.', 
        x: 1300, y: 1000, 
        req: 'root1', owned: false, img: 'images/Korpus.png' 
    },
    { 
        id: 'branch1_up2', name: 'Сонячні Панелі', tier: 'III', desc: 'Генерація енергії.', 
        x: 1600, y: 1000, 
        req: 'branch1_up1', owned: false, img: 'images/Bataries.png' 
    },
    // Нижня гілка (Надкрилки)
    { 
        id: 'branch1_down1', name: 'Аеро-надкрилки', tier: 'II', desc: 'Стабілізація польоту.', 
        x: 1300, y: 1200, 
        req: 'root1', owned: false, img: 'images/Stabilizator.png' 
    },

    // === ГРУПА 2: Двигуни (Турбіна -> Покращення або Бокові) ===
    // Корінь
    { 
        id: 'root2', name: 'Турбо-нагнітач', tier: 'I', desc: 'Подвійна система нагнітання для максимальної тяги двигуна.', 
        x: 1000, y: 1550, 
        req: null, owned: true, img: 'images/Turbina.png' 
    },
    // Верхнє відгалуження (Покращена турбіна)
    { 
        id: 'branch2_up', name: 'Турбо-Форсаж', tier: 'II', desc: 'Покращена турбіна.', 
        x: 1300, y: 1450, 
        req: 'root2', owned: false, img: 'images/Turbina.png' 
    },
    // Нижнє відгалуження (Бокові турбіни)
    { 
        id: 'branch2_down', name: 'Бокові Рушії', tier: 'II', desc: 'Маневрені турбіни.', 
        x: 1300, y: 1650, 
        req: 'root2', owned: false, img: 'images/Turbina.png' 
    },

    // === ГРУПА 3: Верхівка (Верхівка -> Покращення) ===
    { 
        id: 'root3', name: 'Сенсорний шпиль', tier: 'I', desc: 'Модернізована верхівка з датчиками атмосфери та телеметрією.', 
        x: 1000, y: 1900, 
        req: null, owned: true, img: 'images/Nose.png' 
    },
    { 
        id: 'branch3', name: 'Керамічний Щит', tier: 'II', desc: 'Покращена верхівка.', 
        x: 1300, y: 1900, 
        req: 'root3', owned: false, img: 'images/Nose.png' 
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
    // Дерево тепер простягається по Y від 1000 до 1900.
    // Середина дерева по Y ~ 1500
    // Середина по X ~ 1300
    const treeCenterX = 1300; 
    const treeCenterY = 1500;

    // Центр екрану користувача
    const screenCenterX = window.innerWidth / 2;
    const screenCenterY = window.innerHeight / 2;

    // Зсув
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