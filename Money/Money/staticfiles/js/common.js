function toggleExportOptions() {
    const options = document.getElementById('exportOptions');
    const arrow = document.getElementById('arrow');
    if (options.style.display === 'block') {
        options.style.display = 'none';
        arrow.style.transform = 'rotate(0deg)'; // 向上箭头
    } else {
        options.style.display = 'block';
        arrow.style.transform = 'rotate(180deg)'; // 向下箭头
    }
}

// 点击页面其他地方时隐藏菜单
document.addEventListener('click', function (event) {
    const options = document.getElementById('exportOptions');
    const button = document.querySelector('.export-button');
    if (!button.contains(event.target) && !options.contains(event.target)) {
        options.style.display = 'none';
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const spinner = document.getElementById('loadingSpinner');
    spinner.style.display = 'block';
    setTimeout(() => {
        spinner.style.display = 'none';
    }, 1000);
});


function updateBeijingTime() {
    const now = new Date();
    const utcOffset = now.getTimezoneOffset() * 60000;
    const beijingOffset = 8 * 3600000; // 北京时间是 UTC+8
    const beijingTime = new Date(now.getTime() + utcOffset + beijingOffset);
    const formattedTime = beijingTime.toLocaleString('zh-CN', {hour12: false});
    document.getElementById('beijing-time').textContent = `北京时间: ${formattedTime}`;
}

document.addEventListener("DOMContentLoaded", function () {
    updateBeijingTime();
    setInterval(updateBeijingTime, 1000); // 每秒钟更新一次
});

document.addEventListener("DOMContentLoaded", function () {
    document.body.classList.add('loaded');
});