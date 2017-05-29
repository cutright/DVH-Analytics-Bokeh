"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var underscore_1 = require("underscore");
function createElement(type, props) {
    var children = [];
    for (var _i = 2; _i < arguments.length; _i++) {
        children[_i - 2] = arguments[_i];
    }
    var elem;
    if (type === "fragment") {
        elem = document.createDocumentFragment();
    }
    else {
        elem = document.createElement(type);
        for (var k in props) {
            var v = props[k];
            if (k === "className")
                k = "class";
            if (k === "class" && underscore_1.isArray(v))
                v = v.filter(function (c) { return c != null; }).join(" ");
            if (v == null || underscore_1.isBoolean(v) && !v)
                continue;
            elem.setAttribute(k, v);
        }
    }
    for (var _a = 0, _b = underscore_1.flatten(children, true); _a < _b.length; _a++) {
        var v = _b[_a];
        if (v instanceof HTMLElement)
            elem.appendChild(v);
        else if (underscore_1.isString(v))
            elem.appendChild(document.createTextNode(v));
    }
    return elem;
}
exports.createElement = createElement;
