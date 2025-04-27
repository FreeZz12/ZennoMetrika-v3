// ==UserScript==
// @name         get haptcha params
// @namespace    http://tampermonkey.net/
// @version      2025-04-25
// @description  try to take over the world!
// @author       You
// @match        https://*/*
// @icon         data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    let hCaptchaInstance;

    Object.defineProperty(window, "hcaptcha", {
        get: function () {
            return hCaptchaInstance;
        },
        set: function (e) {
            hCaptchaInstance = e;

            let originalRenderFunc = e.render;

            hCaptchaInstance.render = function (container, opts) {
                createHCaptchaWidget(container, opts);
                return originalRenderFunc(container, opts);
            };
        },
    });

    let createHCaptchaWidget = function (container, opts) {
        if (opts.callback !== undefined && typeof opts.callback === "function") {
            let key = "hcaptchaCallback" + Date.now();
            window[key] = opts.callback;
            opts.callback = key;
        }

        const callbackTypes = ['onSuccess', 'onError', 'onExpire', 'onClose', 'onChalExpired', 'onOpen'];

        callbackTypes.forEach(type => {
            if (opts[type] !== undefined && typeof opts[type] === "function") {
                let key = "hcaptcha" + type + Date.now();
                window[key] = opts[type];
                opts[type] = key;
                console.log(`Found ${type} callback:`, key);
            }
        });

        let originalSetCallback = hCaptchaInstance.setCallback;
        hCaptchaInstance.setCallback = function(widgetId, callbackName, callbackFunction) {
            console.log(`Setting callback via API: ${callbackName} for widget ${widgetId}`);
            return originalSetCallback(widgetId, callbackName, callbackFunction);
        };

        // Далее обычный код
        let widgetInfo = {
            captchaType: "hcaptcha",
            widgetId: 0,
            containerId: container,
            sitekey: opts.sitekey,
            callback: opts.callback,
            // Добавляем информацию о всех найденных callbacks
            additionalCallbacks: callbackTypes.filter(type => opts[type]).map(type => ({ type, name: opts[type] }))
        };

        console.log(widgetInfo);
    }

})();
