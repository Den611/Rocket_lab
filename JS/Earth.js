const tg = window.Telegram.WebApp;
tg.expand();

// Відображення імені користувача
if (tg.initDataUnsafe.user) {
    const userElement = document.querySelector('.logo span'); // Припускаю, що спан для імені там є
    if(userElement) {
        userElement.innerText = `👨‍🚀 ${tg.initDataUnsafe.user.username.toUpperCase()}`;
    }
}

const rocketState = {
    nose: 1,     // є
    body: 1,     // є
    engine: 1,   // маленька турбіна
    cabin: 0,
    cargo: 0,
    solar: 0,
    fins: 0,
    booster: 0
};

// Змінна, що пам'ятає, який модуль зараз вибрано
let selectedModuleKey = null;

document.addEventListener("DOMContentLoaded", () => {
    initHyperSpace();
    initInteractions();
    initNavigation();
    updateRocketVisuals(); // Малюємо ракету при старті
});

// --- ОНОВЛЕННЯ ГРАФІКИ (CSS КЛАСИ) ---
function updateRocketVisuals() {
    // Проходимо по кожному модулю в нашому стані
    for (const [key, level] of Object.entries(rocketState)) {
        // Знаходимо елементи (деякі модулі мають по 2 деталі, як fins або boosters)
        // Використовуємо селектор атрибута, щоб знайти всі частини
        const elements = document.querySelectorAll(`[data-module="${key}"]`);
        
        elements.forEach(el => {
            // Очищаємо старі класи рівнів
            el.classList.remove('tier-0', 'tier-1', 'tier-2');
            
            // Додаємо актуальний клас
            el.classList.add(`tier-${level}`);
            
            // Якщо це рівень 0 (креслення), показуємо його (в CSS ми зробили його display:flex, але прозорим)
            // Якщо раніше ми робили display:none, то тепер ми керуємо видимістю через класи tier
            if (level > 0) {
               el.style.display = ''; // Скидаємо inline style, якщо був
            } else {
               // Для Cargo/Fins/Solar важливо, щоб блок фізично був присутній для кліку,
               // тому ми прибираємо display:none, який міг бути в старому CSS
               el.style.display = 'flex'; 
               if(key === 'fins' || key === 'solar' || key === 'booster') el.style.display = 'block';
            }
        });
    }
}

// --- ЛОГІКА АПГРЕЙДУ ---
function upgradeSelectedModule() {
    if (!selectedModuleKey) return; // Нічого не вибрано

    const currentLevel = rocketState[selectedModuleKey];
    const btn = document.querySelector('.upgrade-btn');
    
    // Максимальний рівень - 2 (можна змінити)
    if (currentLevel < 2) {
        // Ефект завантаження
        const originalText = btn.innerText;
        btn.innerText = "INSTALLING...";
        
        setTimeout(() => {
            // Підвищуємо рівень
            rocketState[selectedModuleKey]++;
            
            // Оновлюємо вигляд ракети
            updateRocketVisuals();
            
            // Оновлюємо панель інфо (щоб змінилися цифри Integrity/Level)
            refreshInfoPanel(selectedModuleKey);
            
            // Ефект успіху
            btn.innerText = "COMPLETE!";
            setTimeout(() => {
                // Повертаємо текст кнопки залежно від нового рівня
                updateButtonState(rocketState[selectedModuleKey]); 
            }, 1000);

        }, 500); // Швидкий апгрейд (0.5 сек)
    }
}

// Допоміжна функція оновлення тексту кнопки
function updateButtonState(level) {
    const btn = document.querySelector('.upgrade-btn');
    if (level === 0) {
        btn.innerText = "BUILD MODULE (1000 $)";
        btn.style.background = "var(--accent-orange)";
        btn.style.color = "black";
        btn.disabled = false;
    } else if (level === 1) {
        btn.innerText = "UPGRADE TO MK-2 (5000 $)";
        btn.style.background = "rgba(0, 243, 255, 0.1)";
        btn.style.color = "var(--accent-cyan)";
        btn.disabled = false;
    } else {
        btn.innerText = "MAX LEVEL";
        btn.style.background = "var(--accent-green)";
        btn.style.color = "black";
        btn.disabled = true; // Блокуємо кнопку
    }
}

// --- ВЗАЄМОДІЯ ---
function initInteractions() {
    const modules = document.querySelectorAll('.module');
    const panel = document.getElementById('infoPanel');
    const upgradeBtn = document.querySelector('.upgrade-btn');

    // Клік на кнопку апгрейду
    if(upgradeBtn) {
        upgradeBtn.addEventListener('click', upgradeSelectedModule);
    }

    modules.forEach(mod => {
        mod.addEventListener('mouseenter', () => {
            const key = mod.getAttribute('data-module');
            selectedModuleKey = key; // Запам'ятовуємо, що ми зараз дивимось
            
            refreshInfoPanel(key);
            panel.classList.add('active');
        });
        
        // Мобільна адаптація: клік теж вибирає модуль
        mod.addEventListener('click', () => {
             selectedModuleKey = mod.getAttribute('data-module');
             refreshInfoPanel(selectedModuleKey);
        });
    });
}

// Оновлення текстів у правій панелі
function refreshInfoPanel(key) {
    const data = modulesData[key]; // Беремо з вашого об'єкту modulesData
    const level = rocketState[key]; // Поточний рівень (0, 1 або 2)
    
    const pTitle = document.getElementById('panelTitle');
    const pDesc = document.getElementById('panelDesc');
    const barIntegrity = document.getElementById('barIntegrity');
    const valIntegrity = document.getElementById('statIntegrity');
    const barLevel = document.getElementById('barLevel');
    const levelText = document.getElementById('statLevel');
    
    // Змінюємо опис залежно від рівня
    let displayName = data.title;
    let displayDesc = data.desc;
    let integrity = data.integrity;
    
    if (level === 0) {
        displayName += " (Blueprint)";
        displayDesc = "Module not installed. Purchase required.";
        integrity = 0;
    } else if (level === 2) {
        displayName += " MK-II";
        displayDesc += " [UPGRADED PERFORMANCE]";
        integrity = 100;
    }

    pTitle.innerText = displayName;
    pDesc.innerText = displayDesc;
    
    barIntegrity.style.width = `${integrity}%`;
    valIntegrity.innerText = `${integrity}%`;

    // Візуалізація рівня
    const levelPercent = (level / 2) * 100; // 0%, 50%, 100%
    barLevel.style.width = `${levelPercent}%`;
    levelText.innerText = level === 0 ? "NONE" : `MK-${level}`;

    // Оновлюємо кнопку
    updateButtonState(level);
}

// Єдиний слухач завантаження сторінки
document.addEventListener("DOMContentLoaded", () => {
    initHyperSpace();
    initInteractions();
    initNavigation();
});

// --- 1. ФОНОВІ ЗІРКИ ---
function initHyperSpace() {
    const container = document.getElementById('space-container');
    if (!container) return;

    const starCount = 300; 

    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star');

        const x = Math.random() * 100;
        star.style.left = `${x}%`;

        const depth = Math.random();
        let size, duration;

        if (depth > 0.9) { 
            size = Math.random() * 3 + 2; 
            duration = Math.random() * 1 + 0.5; 
            star.style.zIndex = "2"; 
        } else if (depth > 0.6) { 
            size = Math.random() * 2 + 1;
            duration = Math.random() * 2 + 2; 
            if(Math.random() > 0.8) star.classList.add('blue'); 
        } else { 
            size = Math.random() * 1.5 + 0.5; 
            duration = Math.random() * 5 + 5; 
            star.style.opacity = Math.random() * 0.5 + 0.1;
            if(Math.random() > 0.9) star.classList.add('nebula');
        }

        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        star.style.animationDuration = `${duration}s`;
        star.style.animationDelay = `-${Math.random() * 10}s`;

        container.appendChild(star);
    }
}

// --- 2. ДАНІ МОДУЛІВ РАКЕТИ ---
const modulesData = {
    nose: { title: "Avionics Nose Cone", desc: "Aerodynamic cap housing main navigation computer and radar.", integrity: 98, level: 45 },
    cabin: { title: "Crew Command Deck", desc: "Pressurized module for 5 crew members. Radiation shielded.", integrity: 100, level: 60 },
    cargo: { title: "Secure Cargo Hold", desc: "Capacity: 15 Tons. Current payload: Rover Prototypes & Supplies.", integrity: 92, level: 30 },
    solar: { title: "Photovoltaic Array", desc: "Unfolds in orbit. Generates 50kW power for life support.", integrity: 88, level: 55 },
    body: { title: "Main Fuel Tank", desc: "Cryogenic Liquid Hydrogen/Oxygen storage. Thermal padding active.", integrity: 85, level: 40 },
    booster: { title: "Solid Rocket Booster", desc: "Provides 80% of lift-off thrust. Separation at altitude 50km.", integrity: 99, level: 25 },
    fins: { title: "Titanium Grid Fins", desc: "Hypersonic stabilization for atmospheric re-entry guiding.", integrity: 78, level: 35 },
    engine: { title: "Raptor-X Engine", desc: "Full flow staged combustion. Currently at 100% thrust output.", integrity: 94, level: 90 }
};

// --- 3. ВЗАЄМОДІЯ (РАКЕТА І ПАНЕЛЬ ІНФО) ---
function initInteractions() {
    const modules = document.querySelectorAll('.module');
    const panel = document.getElementById('infoPanel');
    const pTitle = document.getElementById('panelTitle');
    const pDesc = document.getElementById('panelDesc');
    const barIntegrity = document.getElementById('barIntegrity');
    const valIntegrity = document.getElementById('statIntegrity');
    const barLevel = document.getElementById('barLevel');
    const levelText = document.getElementById('statLevel');

    modules.forEach(mod => {
        // Наведення миші
        mod.addEventListener('mouseenter', () => {
            const key = mod.getAttribute('data-module');
            const data = modulesData[key];
            if (!data) return;

            pTitle.innerText = data.title;
            pDesc.innerText = data.desc;
            
            barIntegrity.style.width = `${data.integrity}%`;
            valIntegrity.innerText = `${data.integrity}%`;
            
            if(data.integrity < 50) barIntegrity.style.background = 'red';
            else barIntegrity.style.background = 'var(--accent-cyan)';

            barLevel.style.width = `${data.level}%`;
            levelText.innerText = `MK-${Math.ceil(data.level/10)}`;

            panel.classList.add('active');
        });

        // Клік (ефект)
        mod.addEventListener('click', () => {
            mod.style.filter = "brightness(2) drop-shadow(0 0 20px white)";
            setTimeout(() => {
                mod.style.filter = "";
            }, 150);
        });
    });
}

// --- 4. НАВІГАЦІЯ (ПЛАНЕТИ ТА ПЕРЕХІД) ---
function initNavigation() {
    // 1. ЛОГІКА КЛІКУ ПО ПЛАНЕТАХ (Миттєвий перехід)
    const planets = document.querySelectorAll('.planet-item');
    
    planets.forEach(planet => {
        planet.addEventListener('click', () => {
            const planetName = planet.querySelector('.planet-name').innerText.trim();
            let targetPage = '';

            // Визначаємо, на який файл переходити при кліку на планету
            switch (planetName) {
                case 'EARTH':
                    // Якщо це головна, то зазвичай це index.html або earth.html
                    targetPage = 'index.html'; 
                    break;
                case 'MOON':
                    targetPage = 'moon.html';
                    break;
                case 'MARS':
                    targetPage = 'mars.html';
                    break;
                case 'JUPITER':
                    targetPage = 'jupiter.html'; // Або jupiter.html (як назвеш файл)
                    break;
            }

            // Переходимо
            if (targetPage) {
                console.log(`Navigating to planet view: ${targetPage}`);
                window.location.href = targetPage;
            }
        });
    });

    // 2. ЛОГІКА КНОПКИ "ДЕРЕВО РОЗРОБОК"
    // Кнопка дивиться, яка планета ЗАРАЗ активна на сторінці, і веде до її дерева
    const treeBtn = document.querySelector('.tech-tree-btn');
    if (treeBtn) {
        treeBtn.addEventListener('click', () => {
            const activePlanet = document.querySelector('.planet-item.active');
            
            if (activePlanet) {
                const planetName = activePlanet.querySelector('.planet-name').innerText.trim();
                let treeFile = '';

                switch (planetName) {
                    case 'EARTH': treeFile = 'tree_Earth.html'; break;
                    case 'MOON': treeFile = 'tree_Moon.html'; break;
                    case 'MARS': treeFile = 'tree_Mars.html'; break;
                    case 'JUPITER': treeFile = 'tree_Jupiter.html'; break;
                }
                
                if (treeFile) {
                    console.log(`Navigating to tech tree: ${treeFile}`);
                    window.location.href = treeFile;
                }
            }
        });
    }
}


