"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var DOM = require("core/dom");
exports.default = function (props) {
    var title, value;
    if (props.title != null) {
        if (props.title.length != 0) {
            title = DOM.createElement("label", { for: props.id },
                " ",
                props.title,
                ": ");
        }
        value = DOM.createElement("input", { type: "text", id: props.id, readonly: true });
    }
    return (DOM.createElement("div", { class: "bk-slider-parent" },
        title,
        value,
        DOM.createElement("div", { class: "bk-slider-" + props.orientation },
            DOM.createElement("div", { class: "slider", id: props.id }))));
};
