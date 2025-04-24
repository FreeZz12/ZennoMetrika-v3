// ==UserScript==
// @name         EventListenerMessage
// @namespace    http://tampermonkey.net/
// @version      2025-04-17
// @description  try to take over the world!
// @author       You
// @match        *
// @icon         https://www.google.com/s2/favicons?sz=64&domain=google.com
// @grant        none
// ==/UserScript==

(function() {
    'use strict';
    window.addEventListener('message', function(e) {
        console.log('event', e);
        console.log('data', e.data);
        console.log('origin', e.origin);
        });
})();