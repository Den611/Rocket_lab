const canvas = document.getElementById('canvas');
const viewport = document.getElementById('viewport');

// Точний розрахунок центру для розташування модулів (1400px-1600px) посередині
let currentX = (window.innerWidth / 2) - 1600; 
let currentY = (window.innerHeight / 2) - 1500; 

let isDragging = false;
let startX, startY;

canvas.style.left = currentX + 'px';
canvas.style.top = currentY + 'px';

const treeNodes = [
    { id: 'gu1', name: 'Heavy-X Control', x: 1400, y: 1300, tier: 'I', desc: 'Блок керування з ілюмінатором.' },
    { id: 'gu2', name: 'AI Neuro-Pilot', x: 1700, y: 1300, tier: 'V', req: 'gu1', desc: 'Автоматичне коригування курсу.' },
    { id: 'nc1', name: 'Payload Shell', x: 1400, y: 1420, tier: 'I', desc: 'Стандартний обтікач.' },
    { id: 'h1', name: 'Heavy-X Frame', x: 1700, y: 1420, tier: 'III', req: 'nc1', desc: 'Посилений титановий корпус.' },
    { id: 'p1', name: 'Solar Arrays', x: 1400, y: 1540, tier: 'II', desc: 'Сонячні панелі для живлення.' },
    { id: 'p2', name: 'Active Control Fins', x: 1700, y: 1540, tier: 'IV', req: 'p1', desc: 'Аеродинамічні рулі.' },
    { id: 'e1', name: 'Chemical Engine', x: 1400, y: 1660, tier: 'I', desc: 'Маршовий двигун Heavy-X.' },
    { id: 'e2', name: 'Dual Side Boosters', x: 1700, y: 1660, tier: 'IV', req: 'e1', desc: 'Бічні прискорювачі.' }
];

viewport.addEventListener('mousedown', (e) => {
    if (e.target.closest('.node')) return;
    isDragging = true;
    startX = e.clientX - currentX;
    startY = e.clientY - currentY;
});

window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    let nextX = e.clientX - startX;
    let nextY = e.clientY - startY;

    // Обмеження руху (щоб дерево не тікало за межі сітки)
    if (nextX > 200) nextX = 200;
    if (nextX < -2200) nextX = -2200;
    if (nextY > 300) nextY = 300;
    if (nextY < -2200) nextY = -2200;

    currentX = nextX;
    currentY = nextY;
    canvas.style.left = currentX + 'px';
    canvas.style.top = currentY + 'px';
});

window.addEventListener('mouseup', () => isDragging = false);

function init() {
    treeNodes.forEach(node => {
        const div = document.createElement('div');
        div.className = 'node';
        div.id = `node-${node.id}`;
        div.style.left = node.x + 'px';
        div.style.top = node.y + 'px';
        div.innerHTML = `<div><small>TIER ${node.tier}</small><br><b>${node.name}</b></div>`;
        
        div.onclick = (e) => {
            e.stopPropagation();
            highlightPath(node.id);
            openPanel(node);
        };
        
        canvas.appendChild(div);
        if (node.req) drawLine(node);
    });
}

function drawLine(node) {
    const parent = treeNodes.find(n => n.id === node.req);
    const line = document.createElement('div');
    line.className = 'line';
    line.id = `line-${node.id}`;
    const dx = node.x - parent.x;
    const dy = node.y - parent.y;
    const dist = Math.sqrt(dx*dx + dy*dy);
    line.style.width = (dist - 180) + 'px';
    line.style.left = (parent.x + 180) + 'px';
    line.style.top = (parent.y + 37) + 'px';
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
    document.getElementById('node-name').innerText = node.name;
    document.getElementById('node-tier').innerText = `TIER ${node.tier}`;
    document.getElementById('node-desc').innerText = node.desc;
    document.getElementById('info-panel').classList.add('active');
}

function closePanel() {
    document.getElementById('info-panel').classList.remove('active');
    document.querySelectorAll('.node, .line').forEach(el => el.classList.remove('highlight'));
}

window.onload = init;