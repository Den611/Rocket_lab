const tg = window.Telegram.WebApp;
tg.expand(); // Розгорнути на весь екран

// Відображення імені користувача замість статичного тексту
if (tg.initDataUnsafe.user) {
    document.querySelector('.logo').innerText = `👨‍🚀 ${tg.initDataUnsafe.user.username.toUpperCase()}`;
}

document.addEventListener("DOMContentLoaded", () => {
    initHyperSpace();
});

function initHyperSpace() {
    const container = document.getElementById('space-container');
    
    if (!container) {
        console.error("Помилка: Не знайдено елемент #space-container");
        return;
    }

    const starCount = 300; // Кількість зірок

    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star');

        // 1. Випадкова позиція по ширині (0% - 100%)
        const x = Math.random() * 100;
        star.style.left = `${x}%`;

        // 2. Визначаємо глибину (швидкість і розмір)
        const depth = Math.random();
        let size, duration;

        if (depth > 0.9) { 
            // Ближній шар (найшвидші)
            size = Math.random() * 3 + 2; // 2px - 5px
            duration = Math.random() * 1 + 0.5; // 0.5s - 1.5s
            star.style.zIndex = "2"; // Поверх інших зірок
        } else if (depth > 0.6) { 
            // Середній шар
            size = Math.random() * 2 + 1;
            duration = Math.random() * 2 + 2; 
            if(Math.random() > 0.8) star.classList.add('blue'); // Іноді блакитні
        } else { 
            // Далекий шар (повільні)
            size = Math.random() * 1.5 + 0.5; 
            duration = Math.random() * 5 + 5; // 5s - 10s
            star.style.opacity = Math.random() * 0.5 + 0.1;
            if(Math.random() > 0.9) star.classList.add('nebula');
        }

        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        
        // Швидкість анімації
        star.style.animationDuration = `${duration}s`;
        
        // ВАЖЛИВО: Від'ємна затримка. 
        // Це змушує зірку думати, що вона почала летіти 5 секунд тому.
        // Завдяки цьому при відкритті сайту зорі вже по всьому екрану.
        star.style.animationDelay = `-${Math.random() * 10}s`;

        container.appendChild(star);
    }
}

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

document.querySelectorAll('.planet-item').forEach(p => {
    p.addEventListener('click', () => {
        document
          .querySelectorAll('.planet-item')
          .forEach(x => x.classList.remove('active'));

        p.classList.add('active');

        console.log('Load level:', p.querySelector('.planet-name').innerText);
    });
});