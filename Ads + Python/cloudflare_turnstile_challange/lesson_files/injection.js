(() => {
    window.turnParams = null;

    // Функция для перехвата turnstile
    const checkTurnstile = setInterval(() => {
        if (window.turnstile) {
            clearInterval(checkTurnstile);

            // Сохраняем оригинальный метод render
            const originalRender = window.turnstile.render;

            // Заменяем метод render на наш перехватчик
            window.turnstile.render = function (container, options) {
                // Собираем параметры
                let params = {
                    sitekey: options.sitekey,
                    pageurl: window.location.href,
                    data: options.cData,
                    pagedata: options.chlPageData,
                    action: options.action,
                    userAgent: navigator.userAgent,
                    callback: options.callback ? options.callback.name || 'anonymous function' : 'undefined',
                    'expired-callback': options['expired-callback'] ? options['expired-callback'].name || 'anonymous function' : 'undefined',
                    'error-callback': options['error-callback'] ? options['error-callback'].name || 'anonymous function' : 'undefined',
                    json: 1
                };

                window.turnParams = params;

                // Сохраняем колбек в глобальную переменную
                window.cfCallback = options.callback;

                // Вызываем оригинальный метод
                return originalRender.apply(this, arguments);
            };
        }
    }, 50);
})();

