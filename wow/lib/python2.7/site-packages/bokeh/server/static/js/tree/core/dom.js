"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var types_1 = require("./util/types");
var _createElement = function (tag) { return function (attrs) {
    if (attrs === void 0) { attrs = {}; }
    var children = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        children[_i - 1] = arguments[_i];
    }
    var element;
    if (tag === "fragment") {
        // XXX: this is wrong, but the the common super type of DocumentFragment and HTMLElement is
        // Node, which doesn't support classList, style, etc. attributes.
        element = document.createDocumentFragment();
    }
    else {
        element = document.createElement(tag);
        for (var attr in attrs) {
            var value = attrs[attr];
            if (value == null || types_1.isBoolean(value) && !value)
                continue;
            if (attr === "class" && types_1.isArray(value)) {
                for (var _a = 0, _b = value; _a < _b.length; _a++) {
                    var cls = _b[_a];
                    if (cls != null)
                        element.classList.add(cls);
                }
                continue;
            }
            if (attr === "style" && types_1.isObject(value)) {
                for (var prop in value) {
                    element.style[prop] = value[prop];
                }
                continue;
            }
            element.setAttribute(attr, value);
        }
    }
    function append(child) {
        if (child instanceof HTMLElement)
            element.appendChild(child);
        else if (types_1.isString(child))
            element.appendChild(document.createTextNode(child));
        else if (child != null && child !== false)
            throw new Error("expected an HTMLElement, string, false or null, got " + JSON.stringify(child));
    }
    for (var _c = 0, children_1 = children; _c < children_1.length; _c++) {
        var child = children_1[_c];
        if (types_1.isArray(child)) {
            for (var _d = 0, child_1 = child; _d < child_1.length; _d++) {
                var _child = child_1[_d];
                append(_child);
            }
        }
        else
            append(child);
    }
    return element;
}; };
function createElement(tag, attrs) {
    var children = [];
    for (var _i = 2; _i < arguments.length; _i++) {
        children[_i - 2] = arguments[_i];
    }
    return _createElement(tag).apply(void 0, [attrs].concat(children));
}
exports.createElement = createElement;
exports.div = _createElement("div"), exports.span = _createElement("span"), exports.link = _createElement("link"), exports.style = _createElement("style"), exports.a = _createElement("a"), exports.p = _createElement("p"), exports.pre = _createElement("pre"), exports.input = _createElement("input"), exports.label = _createElement("label"), exports.canvas = _createElement("canvas"), exports.ul = _createElement("ul"), exports.ol = _createElement("ol"), exports.li = _createElement("li");
function show(element) {
    element.style.display = "";
}
exports.show = show;
function hide(element) {
    element.style.display = "none";
}
exports.hide = hide;
function empty(element) {
    var child;
    while (child = element.firstChild) {
        element.removeChild(child);
    }
}
exports.empty = empty;
function position(element) {
    return {
        top: element.offsetTop,
        left: element.offsetLeft,
    };
}
exports.position = position;
function offset(element) {
    var rect = element.getBoundingClientRect();
    return {
        top: rect.top + window.pageYOffset - document.documentElement.clientTop,
        left: rect.left + window.pageXOffset - document.documentElement.clientLeft,
    };
}
exports.offset = offset;
function replaceWith(element, replacement) {
    var parent = element.parentNode;
    if (parent != null) {
        parent.replaceChild(replacement, element);
    }
}
exports.replaceWith = replaceWith;
