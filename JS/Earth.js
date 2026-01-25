const tg = window.Telegram.WebApp;
tg.expand();

// Відображення імені користувача
if (tg.initDataUnsafe.user) {
    const userElement = document.querySelector('.logo span'); 
    if(userElement) {
        userElement.innerText = `👨‍🚀 ${tg.initDataUnsafe.user.username.toUpperCase()}`;
    }
}

// --- 1. НАЛАШТУВАННЯ СТАРТОВОГО СТАНУ (ДЕФОЛТ) ---
// Це те, як виглядає ракета у "новачка"
const defaultRocketState = {
    nose: 1,    // Є
    body: 1,    // Є
    engine: 1,  // Є
    fins: 1,    // Є
    // Все інше - 0 (ПРИХОВАНО)
    cabin: 0,
    cargo: 0,
    solar: 0,
    booster: 0
};

// --- 2. ФУНКЦІЯ ЗАВАНТАЖЕННЯ ---
function loadRocketState() {
    const savedData = localStorage.getItem('myRocketSave');
    
    if (savedData) {
        // Якщо є збереження - беремо його
        return JSON.parse(savedData);
    } else {
        // Якщо немає - беремо дефолтний набір (обрізаний)
        return JSON.parse(JSON.stringify(defaultRocketState));
    }
}

// Ініціалізуємо глобальну змінну ОДИН РАЗ при старті
let rocketState = loadRocketState();

// Змінна для вибраного модуля
let selectedModuleKey = null;

document.addEventListener("DOMContentLoaded", () => {
    console.log('🚀 Rocket Lab Loading...');
    console.log('📦 Loaded State:', rocketState);
    
    initHyperSpace();
    updateRocketVisuals(); // Малюємо ракету
    initInteractions();
    initNavigation();
    
    console.log('✅ Rocket Lab Ready!');
});

// --- 3. ОНОВЛЕННЯ ГРАФІКИ ---
function updateRocketVisuals() {
    // Використовуємо глобальну змінну rocketState
    for (const [key, level] of Object.entries(rocketState)) {
        
        // Знаходимо всі елементи (і ліві, і праві частини)
        const elements = document.querySelectorAll(`[data-module="${key}"]`);
        
        elements.forEach(el => {
            // Очищаємо класи рівнів
            el.classList.remove('tier-0', 'tier-1', 'tier-2');
            
            if (level > 0) {
                // ЯКЩО МОДУЛЬ Є:
                el.classList.add(`tier-${level}`);
                el.style.display = ''; // Повертаємо стандартне відображення (flex/block)
                
                // Фікс для елементів, які в CSS можуть мати display: none
                if (window.getComputedStyle(el).display === 'none') {
                     el.style.display = 'block'; 
                }
            } else {
                // ЯКЩО МОДУЛЯ НЕМАЄ (Рівень 0):
                el.style.display = 'none'; // Жорстко ховаємо
            }
        });
    }
}

// --- ЛОГІКА АПГРЕЙДУ (Тут поки імітація) ---
function upgradeSelectedModule() {
    if (!selectedModuleKey) return; 

    // Тут ти можеш додати логіку переходу в дерево, якщо модуль == 0
    if (rocketState[selectedModuleKey] === 0) {
        alert("Цей модуль ще не встановлено! Перейдіть у Дерево Розробок.");
        return;
    }

    const currentLevel = rocketState[selectedModuleKey];
    const btn = document.querySelector('.upgrade-btn');
    
    if (currentLevel < 2) {
        const originalText = btn.innerText;
        btn.innerText = "INSTALLING...";
        
        setTimeout(() => {
            rocketState[selectedModuleKey]++;
            localStorage.setItem('myRocketSave', JSON.stringify(rocketState)); // Зберігаємо прогрес
            
            updateRocketVisuals();
            refreshInfoPanel(selectedModuleKey);
            
            btn.innerText = "COMPLETE!";
            setTimeout(() => {
                updateButtonState(rocketState[selectedModuleKey]); 
            }, 1000);
        }, 500); 
    }
}

// --- ДОПОМІЖНІ ФУНКЦІЇ ---
function updateButtonState(level) {
    const btn = document.querySelector('.upgrade-btn');
    if (level === 0) {
        btn.innerText = "LOCKED (RESEARCH NEEDED)";
        btn.style.background = "#333";
        btn.style.color = "#888";
        // btn.disabled = true; // Можна розблокувати, якщо хочеш щоб кнопка вела в дерево
    } else if (level === 1) {
        btn.innerText = "UPGRADE TO MK-2 (5000 $)";
        btn.style.background = "rgba(0, 243, 255, 0.1)";
        btn.style.color = "var(--accent-cyan)";
        btn.disabled = false;
    } else {
        btn.innerText = "MAX LEVEL";
        btn.style.background = "var(--accent-green)";
        btn.style.color = "black";
        btn.disabled = true;
    }
}

function initInteractions() {
    const modules = document.querySelectorAll('.module');
    const panel = document.getElementById('infoPanel');
    const upgradeBtn = document.querySelector('.upgrade-btn');

    if(upgradeBtn) {
        upgradeBtn.addEventListener('click', upgradeSelectedModule);
    }

    modules.forEach(mod => {
        mod.addEventListener('mouseenter', () => {
            const key = mod.getAttribute('data-module');
            selectedModuleKey = key;
            refreshInfoPanel(key);
            panel.classList.add('active');
        });
        
        mod.addEventListener('click', () => {
             selectedModuleKey = mod.getAttribute('data-module');
             refreshInfoPanel(selectedModuleKey);
        });
    });
}

function refreshInfoPanel(key) {
    const data = modulesData[key]; 
    const level = rocketState[key]; 
    
    const pTitle = document.getElementById('panelTitle');
    const pDesc = document.getElementById('panelDesc');
    const barIntegrity = document.getElementById('barIntegrity');
    const valIntegrity = document.getElementById('statIntegrity');
    const barLevel = document.getElementById('barLevel');
    const levelText = document.getElementById('statLevel');
    
    let displayName = data.title;
    let displayDesc = data.desc;
    let integrity = data.integrity;
    
    if (level === 0) {
        displayName += " (Locked)";
        displayDesc = "Module not acquired yet. Visit Tech Tree.";
        integrity = 0;
    } else if (level === 2) {
        displayName += " MK-II";
        displayDesc += " [UPGRADED]";
        integrity = 100;
    }

    pTitle.innerText = displayName;
    pDesc.innerText = displayDesc;
    barIntegrity.style.width = `${integrity}%`;
    valIntegrity.innerText = `${integrity}%`;
    
    const levelPercent = (level / 2) * 100;
    barLevel.style.width = `${levelPercent}%`;
    levelText.innerText = level === 0 ? "NONE" : `MK-${level}`;

    updateButtonState(level);
}

// --- НАВІГАЦІЯ ---
function initNavigation() {
    // 1. Кнопки планет (EARTH, MOON, MARS...)
    const planets = document.querySelectorAll('.planet-item');
    
    planets.forEach(planet => {
        planet.addEventListener('click', () => {
            // Шукаємо текст всередині кнопки (наприклад, "MOON")
            const nameElement = planet.querySelector('.planet-name');
            if (!nameElement) return;

            const name = nameElement.innerText.trim();
            let targetPage = '';

            // Визначаємо куди переходити
            switch (name) {
                case 'EARTH': 
                    targetPage = 'index.html'; 
                    break;
                case 'MOON':  
                    targetPage = 'moon.html'; 
                    break;
                case 'MARS':  
                    targetPage = 'mars.html'; 
                    break;
                case 'JUPITER': 
                    targetPage = 'jupiter.html'; 
                    break;
                default:
                    console.log('Unknown planet:', name);
            }

            // Якщо сторінка визначена — переходимо
            if (targetPage) {
                console.log(`Navigating to: ${targetPage}`);
                window.location.href = targetPage;
            }
        });
    });

    // 2. Кнопка Дерева Розробок
    const treeBtn = document.querySelector('.tech-tree-btn');
    if (treeBtn) {
        treeBtn.addEventListener('click', () => {
            // Перевіряємо, яка планета зараз активна (має клас .active)
            // Якщо ми на index.html, то активна Earth
            const activePlanet = document.querySelector('.planet-item.active');
            let treeFile = 'tree_Earth.html'; // Дефолт

            if (activePlanet) {
                const planetName = activePlanet.querySelector('.planet-name').innerText.trim();
                if (planetName === 'MOON') treeFile = 'tree_Moon.html';
                else if (planetName === 'MARS') treeFile = 'tree_Mars.html';
                else if (planetName === 'JUPITER') treeFile = 'tree_Jupiter.html';
            }
            
            window.location.href = treeFile;
        });
    }
}

// --- ФОНОВІ ЗІРКИ ---
function initHyperSpace() {
    const container = document.getElementById('space-container');
    if (!container) return;

    // Очищаємо, щоб не накладалося
    container.innerHTML = ''; 

    const starCount = 300; 

    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star');

        // Випадкова позиція по ширині
        const x = Math.random() * 100;
        star.style.left = `${x}%`;

        const depth = Math.random();
        let size, duration;

        // ЛОГІКА ГЛИБИНИ:
        if (depth > 0.9) { 
            // Дуже близько: великі, швидкі, зверху всіх
            size = Math.random() * 3 + 2; 
            duration = Math.random() * 1 + 0.5; // Дуже швидко (0.5 - 1.5 сек)
            star.style.zIndex = "2"; 
        } else if (depth > 0.6) { 
            // Середня дистанція: середній розмір
            size = Math.random() * 2 + 1;
            duration = Math.random() * 2 + 2; // Середня швидкість
            
            // Додаємо блакитні зірки
            if (Math.random() > 0.8) star.classList.add('blue'); 
        } else { 
            // Далеко: маленькі, повільні, тьмяні
            size = Math.random() * 1.5 + 0.5; 
            duration = Math.random() * 5 + 5; // Повільно (5-10 сек)
            star.style.opacity = Math.random() * 0.5 + 0.1;
            
            // Додаємо туманні зірки (nebula)
            if (Math.random() > 0.9) star.classList.add('nebula');
        }

        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        
        // Встановлюємо тривалість польоту
        star.style.animationDuration = `${duration}s`;
        // Випадкова затримка, щоб вони не летіли "стіною"
        star.style.animationDelay = `-${Math.random() * 10}s`;

        container.appendChild(star);
    }
}

// --- ДАНІ МОДУЛІВ ---
const modulesData = {
    nose: { title: "Nose Cone", desc: "Aerodynamic cap.", integrity: 98, level: 10 },
    cabin: { title: "Crew Deck", desc: "Pressurized module.", integrity: 100, level: 60 },
    cargo: { title: "Cargo Hold", desc: "Capacity: 15 Tons.", integrity: 92, level: 30 },
    solar: { title: "Solar Array", desc: "Generates power.", integrity: 88, level: 55 },
    body: { title: "Fuel Tank", desc: "Liquid Hydrogen.", integrity: 85, level: 40 },
    booster: { title: "Solid Booster", desc: "Lift-off thrust.", integrity: 99, level: 25 },
    fins: { title: "Grid Fins", desc: "Stabilization.", integrity: 78, level: 35 },
    engine: { title: "Raptor Engine", desc: "Main propulsion.", integrity: 94, level: 90 }
};