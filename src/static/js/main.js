document.addEventListener('DOMContentLoaded', function () {
    const API_URL = '/api/products/';

    // Элементы управления
    const priceSlider = document.getElementById('price-slider');
    const minRatingInput = document.getElementById('min-rating');
    const minReviewsInput = document.getElementById('min-reviews');
    const orderingSelect = document.getElementById('ordering');
    const tableBody = document.querySelector('#products-table tbody');
    const loader = document.getElementById('loader');

    // Переменные для графиков
    let priceHistogram = null;
    let discountVsRatingChart = null;

    // Инициализация слайдера цен
    noUiSlider.create(priceSlider, {
        start: [0, 200000],
        connect: true,
        step: 1000,
        range: {
            'min': 0,
            'max': 500000
        }
    });

    const priceLowerValue = document.getElementById('price-lower-value');
    const priceUpperValue = document.getElementById('price-upper-value');

    priceSlider.noUiSlider.on('update', function (values) {
        priceLowerValue.innerHTML = parseInt(values[0]);
        priceUpperValue.innerHTML = parseInt(values[1]);
    });

    // Функция для запроса и обновления данных
    const fetchData = async () => {
        loader.classList.add('visible');
        tableBody.innerHTML = '';

        const params = new URLSearchParams();
        const sliderValues = priceSlider.noUiSlider.get();

        // Не добавляем параметры, если они по умолчанию
        if (parseInt(sliderValues[0]) > 0) {
             params.append('min_price', parseInt(sliderValues[0]));
        }
        // Max price filter не реализован на бэке, но можем сделать на фронте
        // params.append('max_price', parseInt(sliderValues[1]));

        if (minRatingInput.value) {
            params.append('min_rating', minRatingInput.value);
        }
        if (minReviewsInput.value) {
            params.append('min_reviews_count', minReviewsInput.value);
        }
        if (orderingSelect.value) {
            params.append('ordering', orderingSelect.value);
        }

        try {
            const response = await fetch(`${API_URL}?${params.toString()}`);
            const data = await response.json();

            // Фильтр по максимальной цене на фронте, так как бэк его не поддерживает
            const maxPrice = parseInt(sliderValues[1]);
            const filteredData = data.filter(p => p.discounted_price <= maxPrice);

            renderTable(filteredData);
            renderCharts(filteredData);
        } catch (error) {
            console.error("Failed to fetch data:", error);
            tableBody.innerHTML = '<tr><td colspan="5">Не удалось загрузить данные.</td></tr>';
        } finally {
            loader.classList.remove('visible');
        }
    };

    // Функция для рендеринга таблицы
    const renderTable = (products) => {
        if (products.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5">Товары не найдены.</td></tr>';
            return;
        }

        const rows = products.map(p => `
            <tr>
                <td>${p.name}</td>
                <td>${p.price} ₽</td>
                <td>${p.discounted_price} ₽</td>
                <td>${p.rating || 'N/A'}</td>
                <td>${p.reviews_count}</td>
            </tr>
        `).join('');
        tableBody.innerHTML = rows;
    };

    // Функция для рендеринга графиков
    const renderCharts = (products) => {
        renderPriceHistogram(products);
        renderDiscountVsRatingChart(products);
    };

    const renderPriceHistogram = (products) => {
        const ctx = document.getElementById('price-histogram').getContext('2d');
        const prices = products.map(p => p.discounted_price);

        const priceRanges = {
          '0-10k': 0, '10k-30k': 0, '30k-60k': 0, '60k-100k': 0, '100k+': 0
        };

        prices.forEach(price => {
            if (price <= 10000) priceRanges['0-10k']++;
            else if (price <= 30000) priceRanges['10k-30k']++;
            else if (price <= 60000) priceRanges['30k-60k']++;
            else if (price <= 100000) priceRanges['60k-100k']++;
            else priceRanges['100k+']++;
        });

        if (priceHistogram) {
            priceHistogram.destroy();
        }

        priceHistogram = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(priceRanges),
                datasets: [{
                    label: 'Количество товаров',
                    data: Object.values(priceRanges),
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: { scales: { y: { beginAtZero: true } } }
        });
    };

    const renderDiscountVsRatingChart = (products) => {
        const ctx = document.getElementById('discount-vs-rating-chart').getContext('2d');
        const chartData = products
            .filter(p => p.rating && p.price > 0 && p.discounted_price < p.price)
            .map(p => ({
                x: p.rating,
                y: ((p.price - p.discounted_price) / p.price) * 100
            }));

        if (discountVsRatingChart) {
            discountVsRatingChart.destroy();
        }

        discountVsRatingChart = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Скидка (%) vs Рейтинг',
                    data: chartData,
                    backgroundColor: 'rgba(255, 99, 132, 0.6)'
                }]
            },
            options: {
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: { display: true, text: 'Рейтинг' }
                    },
                    y: {
                        title: { display: true, text: 'Скидка, %' }
                    }
                }
            }
        });
    };

    // "debounce" для предотвращения слишком частых запросов
    let debounceTimer;
    const debouncedFetch = () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(fetchData, 500);
    };

    // Навешиваем обработчики событий
    priceSlider.noUiSlider.on('change', debouncedFetch);
    minRatingInput.addEventListener('input', debouncedFetch);
    minReviewsInput.addEventListener('input', debouncedFetch);
    orderingSelect.addEventListener('change', fetchData);

    // Первоначальная загрузка данных
    fetchData();
});