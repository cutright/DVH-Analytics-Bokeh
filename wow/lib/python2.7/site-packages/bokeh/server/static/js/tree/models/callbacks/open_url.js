"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var model_1 = require("../../model");
var p = require("core/properties");
var selection_1 = require("core/util/selection");
var templating_1 = require("core/util/templating");
exports.OpenURL = (function (superClass) {
    extend(OpenURL, superClass);
    function OpenURL() {
        return OpenURL.__super__.constructor.apply(this, arguments);
    }
    OpenURL.prototype.type = 'OpenURL';
    OpenURL.define({
        url: [p.String, 'http://']
    });
    OpenURL.prototype.execute = function (data_source) {
        var i, j, len, ref, url;
        ref = selection_1.get_indices(data_source);
        for (j = 0, len = ref.length; j < len; j++) {
            i = ref[j];
            url = templating_1.replace_placeholders(this.url, data_source, i);
            window.open(url);
        }
        return null;
    };
    return OpenURL;
})(model_1.Model);
