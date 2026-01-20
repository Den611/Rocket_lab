const tg = window.Telegram.WebApp;
tg.expand(); // Розгорнути на весь екран

// Відображення імені користувача замість статичного тексту
if (tg.initDataUnsafe.user) {
    document.querySelector('.logo').innerText = `👨‍🚀 ${tg.initDataUnsafe.user.username.toUpperCase()}`;
}

function createStars() {
    const container = document.getElementById('starField');
    const starCount = 200; 

    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star');
        
        // Випадкові координати
        const x = Math.random() * 100;
        const y = Math.random() * 100;
        const size = Math.random() * 2 + 0.5;
        const delay = Math.random() * 5;

        star.style.left = `${x}%`;
        star.style.top = `${y}%`;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.animationDelay = `${delay}s`;
        
        // Деякі зірки блакитні
        if(Math.random() > 0.8) star.style.background = '#a2d9ff';

        container.appendChild(star);
    }
}
createStars();

// --- 2. СИМУЛЯЦІЯ РЕСУРСІВ (НОВЕ) ---
function simulateResources() {
    const energyEl = document.getElementById('resEnergy');
    const fuelEl = document.getElementById('resFuel');
    const oxyEl = document.getElementById('resOxygen');

    // Проста випадкова флуктуація значень
    setInterval(() => {
        // Енергія трохи скаче (98-100%)
        let e = 98 + Math.random() * 2;
        energyEl.innerText = e.toFixed(1) + '%';
        
        // Паливо повільно зменшується
        let f = parseFloat(fuelEl.innerText);
        f -= 0.05;
        if(f < 95) f = 99.9; // Автозаправка
        fuelEl.innerText = f.toFixed(1) + '%';

        // Кисень стабільний
        oxyEl.innerText = '100%';
        if(Math.random() > 0.9) oxyEl.innerText = '99.9%';

    }, 1000);
}
simulateResources();


// --- 3. БАЗА ДАНИХ МОДУЛІВ ---
const modulesData = {
    nose: {
        title: "Avionics Nose Cone",
        desc: "Aerodynamic cap housing main navigation computer and radar.",
        integrity: 98,
        level: 45
    },
    cabin: {
        title: "Crew Command Deck",
        desc: "Pressurized module for 5 crew members. Radiation shielded.",
        integrity: 100,
        level: 60
    },
    cargo: {
        title: "Secure Cargo Hold",
        desc: "Capacity: 15 Tons. Current payload: Rover Prototypes & Supplies.",
        integrity: 92,
        level: 30
    },
    solar: {
        title: "Photovoltaic Array",
        desc: "Unfolds in orbit. Generates 50kW power for life support.",
        integrity: 88,
        level: 55
    },
    body: {
        title: "Main Fuel Tank",
        desc: "Cryogenic Liquid Hydrogen/Oxygen storage. Thermal padding active.",
        integrity: 85,
        level: 40
    },
    booster: {
        title: "Solid Rocket Booster",
        desc: "Provides 80% of lift-off thrust. Separation at altitude 50km.",
        integrity: 99,
        level: 25
    },
    fins: {
        title: "Titanium Grid Fins",
        desc: "Hypersonic stabilization for atmospheric re-entry guiding.",
        integrity: 78,
        level: 35
    },
    engine: {
        title: "Raptor-X Engine",
        desc: "Full flow staged combustion. Currently at 100% thrust output.",
        integrity: 94,
        level: 90
    }
};

// --- 4. ЛОГІКА ІНТЕРАКЦІЇ ---
const modules = document.querySelectorAll('.module');
const panel = document.getElementById('infoPanel');
const pTitle = document.getElementById('panelTitle');
const pDesc = document.getElementById('panelDesc');
const barIntegrity = document.getElementById('barIntegrity');
const valIntegrity = document.getElementById('statIntegrity');
const barLevel = document.getElementById('barLevel');
const levelText = document.getElementById('statLevel');

function updatePanel(key) {
    const data = modulesData[key];
    if (!data) return;

    pTitle.innerText = data.title;
    pDesc.innerText = data.desc;
    
    // Оновлення смуг
    barIntegrity.style.width = `${data.integrity}%`;
    valIntegrity.innerText = `${data.integrity}%`;
    
    // Червоний колір, якщо цілісність низька
    if(data.integrity < 50) barIntegrity.style.background = 'red';
    else barIntegrity.style.background = 'var(--accent-cyan)';

    barLevel.style.width = `${data.level}%`;
    levelText.innerText = `MK-${Math.ceil(data.level/10)}`;

    panel.classList.add('active');
}

// Додавання подій
modules.forEach(mod => {
    mod.addEventListener('mouseenter', () => {
        const key = mod.getAttribute('data-module');
        updatePanel(key);
    });
    
    mod.addEventListener('click', () => {
        // Ефект спалаху при кліку
        mod.style.filter = "brightness(2) drop-shadow(0 0 20px white)";
        setTimeout(() => {
            mod.style.filter = "";
        }, 150);
    });
});