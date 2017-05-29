"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var DOM = require("core/dom");
var types_1 = require("core/util/types");
exports.default = function (props) {
    return (DOM.createElement("fragment", null,
        DOM.createElement("label", { for: props.id },
            " ",
            props.title,
            " "),
        DOM.createElement("select", { class: "bk-widget-form-input", id: props.id, name: props.name }, props.options.map(function (option) {
            var value, label;
            if (types_1.isString(option)) {
                value = label = option;
            }
            else {
                value = option[0], label = option[1];
            }
            var selected = props.value == value;
            return DOM.createElement("option", { selected: selected, value: value }, label);
        }))));
};
