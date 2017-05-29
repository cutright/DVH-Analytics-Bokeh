"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var DOM = require("core/dom");
exports.default = function (props) {
    var active = function (tab) { return tab.id === props.active_tab_id ? "bk-bs-active" : null; };
    return (DOM.createElement("fragment", null,
        DOM.createElement("ul", { class: "bk-bs-nav bk-bs-nav-tabs" }, props.tabs.map(function (tab) {
            return DOM.createElement("li", { class: active(tab) },
                DOM.createElement("a", { href: "#tab-" + tab.id }, tab.title));
        })),
        DOM.createElement("div", { class: "bk-bs-tab-content" }, props.tabs.map(function (tab) { return DOM.createElement("div", { class: ["bk-bs-tab-pane", active(tab)], id: "tab-" + tab.id }); }))));
};
