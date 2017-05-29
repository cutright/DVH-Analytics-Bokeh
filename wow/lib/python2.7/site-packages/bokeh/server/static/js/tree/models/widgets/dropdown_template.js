"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var DOM = require("core/dom");
exports.default = function (props) {
    var classes = ["bk-bs-btn", "bk-bs-btn-" + props.button_type, "bk-bs-dropdown-toggle", "bk-bs-dropdown-btn"];
    return (DOM.createElement("fragment", null,
        DOM.createElement("button", { type: "button", class: classes, "data-bk-bs-toggle": "dropdown" },
            props.label,
            " ",
            DOM.createElement("span", { class: "bk-bs-caret" })),
        DOM.createElement("ul", { class: "bk-bs-dropdown-menu" })));
};
