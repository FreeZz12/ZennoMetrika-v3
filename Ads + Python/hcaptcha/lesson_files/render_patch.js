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

    window.location = "javascript: (" + function () {

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
            console.log('HCaptcha options:', opts);
            if (opts.callback !== undefined && typeof opts.callback === "function") {
                let key = "hcaptchaCallback" + Date.now();
                window[key] = opts.callback;
                opts.callback = key;
            }

            let widgetInfo = {
                captchaType: "hcaptcha",
                widgetId: 0,
                containerId: container,
                sitekey: opts.sitekey,
                callback: opts.callback,
            };

            console.log(widgetInfo);
        }

    } + ")()";
})();
