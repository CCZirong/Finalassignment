function toggleDataOptions() {
    const options = document.getElementById('dataOptions');
    const arrow = document.getElementById('dataArrow');
    const button = document.querySelector('.data-button');

    const isExpanded = options.classList.contains('show');
    options.classList.toggle('show');
    arrow.style.transform = isExpanded ? 'rotate(0deg)' : 'rotate(180deg)';

    button.setAttribute('aria-expanded', !isExpanded);
    options.setAttribute('aria-hidden', isExpanded);
}

document.addEventListener('click', function (event) {
    const options = document.getElementById('dataOptions');
    const button = document.querySelector('.data-button');

    if (!button.contains(event.target) && !options.contains(event.target)) {
        options.classList.remove('show');
        document.getElementById('dataArrow').style.transform = 'rotate(0deg)';
        button.setAttribute('aria-expanded', false);
        options.setAttribute('aria-hidden', true);
    }
});

function toggleStockOptions(stockType) {
    let tableName;
    let buttonText;
    switch (stockType) {
        case 'hk':
            tableName = 'hong_kong_stocks';
            buttonText = '港股';
            break;
        case 'us':
            tableName = 'US_shares_stocks';
            buttonText = '美股';
            break;
        case 'uk':
            tableName = 'Britain_stocks';
            buttonText = '英股';
            break;
        default:
            tableName = 'hong_kong_stocks';
            buttonText = '选择展示数据';
    }

    const button = document.querySelector('.data-button');
    button.innerHTML = `${buttonText} <span id="dataArrow" class="arrow" aria-hidden="true">▲</span>`;

    window.location.href = `{% url 'line' %}?table=${tableName}`;
}

function setButtonTextFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const table = urlParams.get('table') || 'hong_kong_stocks';
    let buttonText;

    switch (table) {
        case 'hong_kong_stocks':
            buttonText = '港股';
            break;
        case 'US_shares_stocks':
            buttonText = '美股';
            break;
        case 'Britain_stocks':
            buttonText = '英股';
            break;
        default:
            buttonText = '选择展示数据';
    }

    const button = document.querySelector('.data-button');
    button.innerHTML = `${buttonText} <span id="dataArrow" class="arrow" aria-hidden="true">▲</span>`;
}

document.addEventListener('DOMContentLoaded', setButtonTextFromURL);


function exportData(format) {
    const urlParams = new URLSearchParams(window.location.search);
    const table = urlParams.get('table') || 'hong_kong_stocks';
    let exportUrl;

    if (format === 'csv') {
        exportUrl = `{% url 'export_csv' %}`;
    } else if (format === 'pdf') {
        exportUrl = `{% url 'export_pdf' %}`;
    }

    window.location.href = `${exportUrl}?table=${table}`;
}

