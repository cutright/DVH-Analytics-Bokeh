"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var _all_models, hasProp = {}.hasOwnProperty;
var models = require("./models/index");
var object_1 = require("./core/util/object");
exports.overrides = {};
_all_models = object_1.clone(models);
exports.Models = function (name) {
    var model, ref;
    model = (ref = exports.overrides[name]) != null ? ref : _all_models[name];
    if (model == null) {
        throw new Error("Model `" + name + "' does not exist. This could be due to a widget or a custom model not being registered before first usage.");
    }
    return model;
};
exports.Models.register = function (name, model) {
    return exports.overrides[name] = model;
};
exports.Models.unregister = function (name) {
    return delete exports.overrides[name];
};
exports.Models.register_models = function (models, force, errorFn) {
    var model, name, results;
    if (force == null) {
        force = false;
    }
    if (errorFn == null) {
        errorFn = null;
    }
    if (models == null) {
        return;
    }
    results = [];
    for (name in models) {
        if (!hasProp.call(models, name))
            continue;
        model = models[name];
        if (force || !_all_models.hasOwnProperty(name)) {
            results.push(_all_models[name] = model);
        }
        else {
            results.push(typeof errorFn === "function" ? errorFn(name) : void 0);
        }
    }
    return results;
};
exports.Models.registered_names = function () {
    return Object.keys(_all_models);
};
exports.index = {};
