
(function() {
    window.test1 = 1;
    const checker = setInterval(() => {
        if (window.turnstile) {
            clearInterval(checker);
            window.test2 = 1;

            const originalRender = window.turnstile.render;
            // логика подмены render
            window.turnstile.render = function(a, b) {
                window.turnParams = {
                    sitekey: b.sitekey,
                    action: b.action,
                    cData: b.cData,
                    chlPageData: b.chlPageData,
                    pageurl: window.location.href,
                    userAgent: navigator.userAgent
                }
                window.cfCallback = b.callback;
                window.test3 = 1;

                return originalRender.apply(this, arguments);
            }
        }
    },50);
})();