let latestUpdateTime = null;
let countdownInterval = null;
let updateIntervalMinutes = 15; // 默认值

async function fetchLatestUpdateTime() {
    try {
        const response = await fetch('/latest-update-time/');
        const data = await response.json();
        const newUpdateTime = new Date(data.latest_update_time);

        // 更新 updateIntervalMinutes 为从服务器获取的 time 值
        updateIntervalMinutes = data.time;

        if (!latestUpdateTime || newUpdateTime.getTime() !== latestUpdateTime.getTime()) {
            latestUpdateTime = newUpdateTime;
            updateCountdown();
        }
    } catch (error) {
        console.error('获取最新更新时间时出错:', error);
    }
}

function updateCountdown() {
    const countdownElement = document.getElementById("countdown");

    if (countdownInterval) {
        clearInterval(countdownInterval);
    }

    countdownInterval = setInterval(() => {
        if (latestUpdateTime) {
            const now = new Date();
            const timeDiff = Math.max(0, now - latestUpdateTime);
            const minutes = Math.floor(timeDiff / 60000);
            const seconds = Math.floor((timeDiff % 60000) / 1000);
            countdownElement.textContent = `${updateIntervalMinutes}分钟自动更新，距离上次更新: ${minutes} 分 ${seconds} 秒`;
        }
    }, 1000);
}

function startScanEffect(card) {
    card.classList.remove('scan');
    void card.offsetWidth;
    card.classList.add('scan');
}

document.addEventListener("DOMContentLoaded", () => {
    setInterval(() => {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            startScanEffect(card);
        });
    }, 5000);
});

setInterval(fetchLatestUpdateTime, 1000);

document.addEventListener("DOMContentLoaded", function () {
    document.body.classList.add('loaded');
});