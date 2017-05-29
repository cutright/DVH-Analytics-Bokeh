"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var DOM = require("core/dom");
exports.default = function (props) {
    var logo;
    if (props.logo != null) {
        var cls = props.logo === "grey" ? "bk-grey" : null;
        logo = DOM.createElement("a", { href: "http://bokeh.pydata.org/", target: "_blank", class: ["bk-logo", "bk-logo-small", cls] });
    }
    return (DOM.createElement("div", { class: ["bk-toolbar-" + props.location, "bk-toolbar-" + props.sticky] },
        logo,
        DOM.createElement("div", { class: 'bk-button-bar' },
            DOM.createElement("div", { class: 'bk-button-bar-list', type: "pan" }),
            DOM.createElement("div", { class: 'bk-button-bar-list', type: "scroll" }),
            DOM.createElement("div", { class: 'bk-button-bar-list', type: "pinch" }),
            DOM.createElement("div", { class: 'bk-button-bar-list', type: "tap" }),
            DOM.createElement("div", { class: 'bk-button-bar-list', type: "press" }),
            DOM.createElement("div", { class: 'bk-button-bar-list', type: "rotate" }),
            DOM.createElement("div", { class: 'bk-button-bar-list', type: "actions" }),
            DOM.createElement("div", { class: 'bk-button-bar-list', type: "inspectors" }),
            DOM.createElement("div", { class: 'bk-button-bar-list', type: "help" }))));
};
