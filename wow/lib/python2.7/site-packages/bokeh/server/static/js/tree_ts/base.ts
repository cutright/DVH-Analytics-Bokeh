var _all_models,
  hasProp = {}.hasOwnProperty;

import * as models from "./models/index";

import {
  clone
} from "./core/util/object";

export var overrides = {};

_all_models = clone(models);

export var Models = function(name) {
  var model, ref;
  model = (ref = overrides[name]) != null ? ref : _all_models[name];
  if (model == null) {
    throw new Error("Model `" + name + "' does not exist. This could be due to a widget or a custom model not being registered before first usage.");
  }
  return model;
};

Models.register = function(name, model) {
  return overrides[name] = model;
};

Models.unregister = function(name) {
  return delete overrides[name];
};

Models.register_models = function(models, force, errorFn) {
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
    if (!hasProp.call(models, name)) continue;
    model = models[name];
    if (force || !_all_models.hasOwnProperty(name)) {
      results.push(_all_models[name] = model);
    } else {
      results.push(typeof errorFn === "function" ? errorFn(name) : void 0);
    }
  }
  return results;
};

Models.registered_names = function() {
  return Object.keys(_all_models);
};

export var index = {};
