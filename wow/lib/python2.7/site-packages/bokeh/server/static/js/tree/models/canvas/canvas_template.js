"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var DOM = require("core/dom");
exports.default = function (props) {
    return (DOM.createElement("fragment", null,
        props.map && DOM.createElement("div", { class: "bk-canvas-map" }),
        DOM.createElement("div", { class: "bk-canvas-events" }),
        DOM.createElement("div", { class: "bk-canvas-overlays" }),
        DOM.createElement("canvas", { class: 'bk-canvas' })));
};
