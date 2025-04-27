() => {
    const captchaIframe = document.querySelector('iframe[data-hcaptcha-widget-id]');
    const widgetId = captchaIframe.getAttribute('data-hcaptcha-widget-id');


    // Создаем объект события MessageEvent
    const messageEvent = new MessageEvent("message", {
        data: {
            source: "hcaptcha",
            label: "challenge-closed",
            id: widgetId,
            contents: {
                event: "challenge-passed",
                response: "тут должен быть токен решения каптчи",
                expiration: 120
            }
        },
        origin: "https://newassets.hcaptcha.com",
        bubbles: true,
    });

    // Отправляем событие в текущее окно
    window.dispatchEvent(messageEvent);
}