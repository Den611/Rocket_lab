// --- 1. ГЕНЕРАЦІЯ ЗІРОК ---
function createStars() {
    const container = document.getElementById('starField');
    const starCount = 150;

    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star');
        
        // Випадкова позиція
        const x = Math.random() * 100;
        const y = Math.random() * 100;
        // Випадковий розмір
        const size = Math.random() * 2 + 1;
        // Випадкова затримка анімації
        const delay = Math.random() * 5;

        star.style.left = `${x}%`;
        star.style.top = `${y}%`;
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.animationDelay = `${delay}s`;

        container.appendChild(star);
    }
}

createStars();

// --- 2. ДАНІ МОДУЛІВ ---
const modulesData = {
    nose: {
        title: "Sensor Array (Nose)",
        desc: "Contains advanced radar and comms systems. Aerodynamic carbon-fiber composite hull.",
        integrity: 85,
        level: 30 
    },
    cabin: {
        title: "Command Module",
        desc: "Life support systems active. Capacity: 3 Astronauts + AI Core. Reinforced glass viewports.",
        integrity: 100,
        level: 50
    },
    body: {
        title: "Fuel Tanks",
        desc: "Liquid Oxygen / Hydrogen storage. Thermal shielding applied for atmospheric re-entry.",
        integrity: 90,
        level: 40
    },
    fins: {
        title: "Stabilizer Fins",
        desc: "Provides atmospheric stability during ascent and descent. Titanium alloy construction.",
        integrity: 75,
        level: 20
    },
    engine: {
        title: "V-2 Ion Thruster",
        desc: "High-efficiency propulsion system. Currently in standby mode. Ready for ignition sequence.",
        integrity: 95,
        level: 80
    }
};

// --- 3. ЛОГІКА ІНТЕРАКЦІЇ ---
const modules = document.querySelectorAll('.module');
const panel = document.getElementById('infoPanel');
const pTitle = document.getElementById('panelTitle');
const pDesc = document.getElementById('panelDesc');
const barIntegrity = document.getElementById('barIntegrity');
const valIntegrity = document.getElementById('statIntegrity');
const barLevel = document.getElementById('barLevel');

// Функція оновлення панелі
function updatePanel(key) {
    const data = modulesData[key];
    if (!data) return;

    pTitle.innerText = data.title;
    pDesc.innerText = data.desc;
    
    // Анімація смуг прогресу
    barIntegrity.style.width = `${data.integrity}%`;
    valIntegrity.innerText = `${data.integrity}%`;
    
    barLevel.style.width = `${data.level}%`;
    
    // Вмикаємо панель (візуально)
    panel.classList.add('active');
}

// Додаємо слухачі подій
modules.forEach(mod => {
    mod.addEventListener('mouseenter', () => {
        const key = mod.getAttribute('data-module');
        updatePanel(key);
    });
    
    mod.addEventListener('click', () => {
        console.log(`Selected: ${mod.getAttribute('data-module')}`);
    });
});