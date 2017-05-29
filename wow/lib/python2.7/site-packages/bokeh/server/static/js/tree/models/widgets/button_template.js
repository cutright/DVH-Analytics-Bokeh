"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var DOM = require("core/dom");
exports.default = function (props) {
    return (DOM.createElement("button", { type: "button", class: "bk-bs-btn bk-bs-btn-" + props.button_type }, props.label));
};
