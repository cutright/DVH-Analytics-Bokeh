/*!
 * jQuery Mousewheel 3.1.13
 *
 * Copyright jQuery Foundation and other contributors
 * Released under the MIT license
 * http://jquery.org/license
 */
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
function fontSize(element) {
    return parseInt(getComputedStyle(element).fontSize, 10) || null;
}
function lineHeight(element) {
    var parent = element.offsetParent || document.body;
    return fontSize(parent) || fontSize(element) || 16;
}
function pageHeight(element) {
    return element.clientHeight; // XXX: should be content height?
}
function getDeltaY(event) {
    var deltaY = -event.deltaY;
    if (event.target instanceof HTMLElement) {
        switch (event.deltaMode) {
            case event.DOM_DELTA_LINE:
                deltaY *= lineHeight(event.target);
                break;
            case event.DOM_DELTA_PAGE:
                deltaY *= pageHeight(event.target);
                break;
        }
    }
    return deltaY;
}
exports.getDeltaY = getDeltaY;
