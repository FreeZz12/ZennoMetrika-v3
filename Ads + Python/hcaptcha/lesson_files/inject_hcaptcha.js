(token) => {
    const captchaIframe = document.querySelector('iframe[data-hcaptcha-widget-id]');
    const widgetId = captchaIframe.getAttribute('data-hcaptcha-widget-id');


    const event = new MessageEvent('message', {
        data: {
            "source": "hcaptcha",
            "label": "challenge-closed",
            "id":  widgetId,
            "contents": {
                "event": "challenge-passed",
                "response": token,
                "expiration": 120
            }
        },
        origin: 'https://newassets.hcaptcha.com',
        bubbles: true
    });
    document.dispatchEvent(event);
    window.hcaptcha.close(widgetId);


    // Также попробуем вызвать close у объекта challenge
    window.hcaptcha.close(widgetId);
}