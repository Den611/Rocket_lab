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
    // === ГРУПА 1: ВЕРХНЯ (Асиметрична) ===
    // 1. Старт
    { 
        id: 'g1_start', name: 'Герметизація', tier: 'I', desc: 'Покращена ізоляція відсіку для захисту вантажу.', 
        x: 1000, y: 1000, 
        req: null, owned: true, img: 'images/Korpus.png' 
    },
    // 2. Лінійне продовження (Точка розвилки)
    { 
        id: 'g1_split', name: 'Processing', tier: 'II', desc: 'Процесор.', 
        x: 1250, y: 1000, 
        req: 'g1_start', owned: false, img: 'images/modules/ai.png' 
    },
    
    // --- ВЕРХНЯ ГІЛКА (2 блоки) ---
    { 
        id: 'g1_up1', name: 'Logic Unit', tier: 'III', desc: 'Логіка.', 
        x: 1500, y: 900, // Вгору
        req: 'g1_split', owned: false, img: 'images/modules/quantum.png' 
    },
    { 
        id: 'g1_up2', name: 'Adv. AI', tier: 'IV', desc: 'Вищий ШІ.', 
        x: 1750, y: 900, // Вправо
        req: 'g1_up1', owned: false, img: 'images/modules/ai.png' 
    },

    // --- НИЖНЯ ГІЛКА (3 блоки - довша) ---
    { 
        id: 'g1_down1', name: 'Hull Plating', tier: 'III', desc: 'Обшивка.', 
        x: 1500, y: 1100, // Вниз
        req: 'g1_split', owned: false, img: 'images/modules/body.png' 
    },
    { 
        id: 'g1_down2', name: 'Armor Layer', tier: 'IV', desc: 'Броня.', 
        x: 1750, y: 1100, // Вправо
        req: 'g1_down1', owned: false, img: 'images/modules/shield.png' 
    },
    { 
        id: 'g1_down3', name: 'Kinetic Shield', tier: 'V', desc: 'Кінетичний щит.', 
        x: 2000, y: 1100, // Ще правіше (найдовша гілка)
        req: 'g1_down2', owned: false, img: 'images/modules/shield.png' 
    },


    // === ГРУПА 2: СЕРЕДНЯ (Коротка розвилка) ===
    { 
        id: 'g2_start', name: 'Покращений Форсаж', tier: 'I', desc: 'Оптимізована камера згоряння для економії палива.', 
        x: 1000, y: 1450, 
        req: null, owned: true, img: 'images/Turbina.png' 
    },
    { 
        id: 'g2_up', name: 'Ion Thruster', tier: 'II', desc: 'Іон.', 
        x: 1250, y: 1350, // Вгору
        req: 'g2_start', owned: false, img: 'images/modules/booster.png' 
    },
    { 
        id: 'g2_down', name: 'Plasma Drive', tier: 'II', desc: 'Плазма.', 
        x: 1250, y: 1550, // Вниз
        req: 'g2_start', owned: false, img: 'images/modules/quantum.png' 
    },


    // === ГРУПА 3: НИЖНЯ (Проста лінія) ===
    { 
        id: 'g3_start', name: 'Нова Верхівка', tier: 'I', desc: 'Посилений титановий конус для пробиття хмар.', 
        x: 1000, y: 1800, 
        req: null, owned: true, img: 'images/Nose.png' 
    },
    { 
        id: 'g3_end', name: 'Cryo Stasis', tier: 'II', desc: 'Кріо.', 
        x: 1250, y: 1800, 
        req: 'g3_start', owned: false, img: 'images/modules/body.png' 
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

document.addEventListener('DOMContentLoaded', () => {
    const backBtn = document.getElementById('dynamic-back-btn');
    const path = window.location.pathname; // Отримуємо поточну адресу
    
    // Об'єкт конфігурації: "де ми є" -> "куди йти"
    const routes = {
        'tree_Earth.html': { url: 'index.html', text: 'ГОЛОВНА' },
        'tree_Moon.html':  { url: 'Moon.html',  text: 'МІСЯЦЬ' },
        'tree_Mars.html':  { url: 'Mars.html',  text: 'МАРС' },
        'tree_Jupiter.html': { url: 'Jupiter.html', text: 'ЮПІТЕР' }
    };

    // Перевіряємо, який файл зараз відкрито
    for (const [key, route] of Object.entries(routes)) {
        if (path.includes(key)) {
            backBtn.href = route.url;
            backBtn.innerHTML = `<span class="arrow">‹</span> ${route.text}`;
            break; 
        }
    }
    
    // Якщо сторінка не знайдена в списку, ведемо на index.html за замовчуванням
    if (backBtn.getAttribute('href') === '#') {
        backBtn.href = 'index.html';
        backBtn.innerHTML = `<span class="arrow">‹</span> MENU`;
    }
});

window.onload = init;