"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var DOM = require("core/dom");
exports.default = function (props) {
    return (DOM.createElement("fragment", null,
        DOM.createElement("label", { for: props.id },
            " ",
            props.title,
            " "),
        DOM.createElement("input", { class: "bk-widget-form-input", type: "text", id: props.id, name: props.name, value: props.value, placeholder: props.placeholder })));
};
