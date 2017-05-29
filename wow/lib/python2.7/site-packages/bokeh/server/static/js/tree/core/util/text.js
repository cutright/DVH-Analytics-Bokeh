"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var cache;
var dom_1 = require("../dom");
cache = {};
exports.get_text_height = function (font) {
    var block, elem, result, text;
    if (cache[font] != null) {
        return cache[font];
    }
    text = dom_1.span({
        style: {
            font: font
        }
    }, "Hg");
    block = dom_1.div({
        style: {
            display: "inline-block",
            width: "1px",
            height: "0px"
        }
    });
    elem = dom_1.div({}, text, block);
    document.body.appendChild(elem);
    try {
        result = {};
        block.style.verticalAlign = "baseline";
        result.ascent = dom_1.offset(block).top - dom_1.offset(text).top;
        block.style.verticalAlign = "bottom";
        result.height = dom_1.offset(block).top - dom_1.offset(text).top;
        result.descent = result.height - result.ascent;
    }
    finally {
        document.body.removeChild(elem);
    }
    cache[font] = result;
    return result;
};
