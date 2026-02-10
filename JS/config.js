// JS/config.js

// 1. Зберігаємо ID при завантаженні
const urlParams = new URLSearchParams(window.location.search);
const GLOBAL_FAMILY_ID = urlParams.get('family_id');

if (GLOBAL_FAMILY_ID) {
    console.log("🔒 Session Active. Family ID:", GLOBAL_FAMILY_ID);
} else {
    console.warn("⚠️ No Family ID found. Navigation might be broken.");
}

// 2. ГЛОБАЛЬНА ФУНКЦІЯ ПЕРЕХОДУ
window.navigateTo = function(page) {
    if (GLOBAL_FAMILY_ID) {
        const separator = page.includes('?') ? '&' : '?';
        window.location.href = `${page}${separator}family_id=${GLOBAL_FAMILY_ID}`;
    } else {
        window.location.href = page;
    }
};

// 3. АВТОМАТИЧНА ОБРОБКА ПОСИЛАНЬ
document.addEventListener('click', function(e) {
    const link = e.target.closest('a');
    if (link && link.href && GLOBAL_FAMILY_ID) {
        if (link.href.startsWith('javascript') || link.href.includes('#')) return;
        try {
            const url = new URL(link.href, window.location.origin);
            if (!url.searchParams.has('family_id')) {
                url.searchParams.set('family_id', GLOBAL_FAMILY_ID);
                link.href = url.toString();
            }
        } catch (err) {}
    }
});