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
    { id: 'root1', name: 'Сталевий Корпус', tier: 'I', desc: 'Базова основа ракети.', x: 1000, y: 1100, req: null, owned: true, img: 'images/Korpus.png', cost: { iron: 0, fuel: 0, coins: 0 } },
    { id: 'branch1_up1', name: 'Вантажний Відсік', tier: 'II', desc: 'Додатковий модуль.', x: 1300, y: 1000, req: 'root1', owned: false, img: 'images/Korpus.png', cost: { iron: 400, fuel: 200, coins: 350 } },
    { id: 'branch1_up2', name: 'Сонячні Панелі', tier: 'III', desc: 'Генерація енергії.', x: 1600, y: 1000, req: 'branch1_up1', owned: false, img: 'images/Bataries.png', cost: { iron: 300, fuel: 100, coins: 450 } },
    { id: 'branch1_down1', name: 'Аеро-надкрилки', tier: 'II', desc: 'Стабілізація польоту.', x: 1300, y: 1200, req: 'root1', owned: false, img: 'images/Stabilizator.png', cost: { iron: 250, fuel: 150, coins: 300 } },
    { id: 'root2', name: 'Турбо-нагнітач', tier: 'I', desc: 'Система нагнітання тяги.', x: 1000, y: 1550, req: null, owned: true, img: 'images/Turbina.png', cost: { iron: 0, fuel: 0, coins: 0 } },
    { id: 'branch2_up', name: 'Турбо-Форсаж', tier: 'II', desc: 'Покращена турбіна.', x: 1300, y: 1450, req: 'root2', owned: false, img: 'images/Turbina.png', cost: { iron: 500, fuel: 400, coins: 600 } },
    { id: 'branch2_down', name: 'Бокові Рушії', tier: 'II', desc: 'Маневрені турбіни.', x: 1300, y: 1650, req: 'root2', owned: false, img: 'images/Turbina.png', cost: { iron: 350, fuel: 250, coins: 400 } },
    { id: 'root3', name: 'Сенсорний шпиль', tier: 'I', desc: 'Телеметрія.', x: 1000, y: 1900, req: null, owned: true, img: 'images/Nose.png', cost: { iron: 0, fuel: 0, coins: 0 } },
    { id: 'branch3', name: 'Керамічний Щит', tier: 'II', desc: 'Захист верхівки.', x: 1300, y: 1900, req: 'root3', owned: false, img: 'images/Nose.png', cost: { iron: 300, fuel: 100, coins: 380 } }
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
            <div class="cost-cell"><span class="cost-icon">🌑</span><span class="cost-value">${c.iron}</span></div>
            <div class="cost-cell"><span class="cost-icon">⚛️</span><span class="cost-value">${c.fuel}</span></div>
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