var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  HasProps
} from "./core/has_props";

import * as p from "./core/properties";

import {
  isString
} from "./core/util/types";

import {
  isEmpty
} from "./core/util/object";

import {
  logger
} from "./core/logging";

export var Model = (function(superClass) {
  extend(Model, superClass);

  function Model() {
    return Model.__super__.constructor.apply(this, arguments);
  }

  Model.prototype.type = "Model";

  Model.define({
    tags: [p.Array, []],
    name: [p.String],
    js_property_callbacks: [p.Any, {}],
    js_event_callbacks: [p.Any, {}],
    subscribed_events: [p.Array, []]
  });

  Model.prototype.initialize = function(options) {
    var callbacks, cb, evt, i, len, ref1;
    Model.__super__.initialize.call(this, options);
    ref1 = this.js_property_callbacks;
    for (evt in ref1) {
      callbacks = ref1[evt];
      for (i = 0, len = callbacks.length; i < len; i++) {
        cb = callbacks[i];
        this.listenTo(this, evt, function() {
          return cb.execute(this);
        });
      }
    }
    this.listenTo(this, 'change:js_event_callbacks', function() {
      return this._update_event_callbacks;
    });
    return this.listenTo(this, 'change:subscribed_events', function() {
      return this._update_event_callbacks;
    });
  };

  Model.prototype._process_event = function(event) {
    var callback, i, len, ref1, ref2;
    if (event.is_applicable_to(this)) {
      event = event._customize_event(this);
      ref2 = (ref1 = this.js_event_callbacks[event.event_name]) != null ? ref1 : [];
      for (i = 0, len = ref2.length; i < len; i++) {
        callback = ref2[i];
        callback.execute(event, {});
      }
      if (this.subscribed_events.some(function(m) {
        return m === event.event_name;
      })) {
        return this.document.event_manager.send_event(event);
      }
    }
  };

  Model.prototype.trigger_event = function(event) {
    var ref1;
    return (ref1 = this.document) != null ? ref1.event_manager.trigger(event.set_model_id(this.id)) : void 0;
  };

  Model.prototype._update_event_callbacks = function() {
    if (this.document == null) {
      logger.warn('WARNING: Document not defined for updating event callbacks');
      return;
    }
    return this.document.event_manager.subscribed_models.push(this.id);
  };

  Model.prototype._doc_attached = function() {
    if (!isEmpty(this.js_event_callbacks) || !isEmpty(this.subscribed_events)) {
      return this._update_event_callbacks();
    }
  };

  Model.prototype.select = function(selector) {
    if (selector.prototype instanceof Model) {
      return this.references().filter(function(ref) {
        return ref instanceof selector;
      });
    } else if (isString(selector)) {
      return this.references().filter(function(ref) {
        return ref.name === selector;
      });
    } else {
      throw new Error("invalid selector");
    }
  };

  Model.prototype.select_one = function(selector) {
    var result;
    result = this.select(selector);
    switch (result.length) {
      case 0:
        return null;
      case 1:
        return result[0];
      default:
        throw new Error("found more than one object matching given selector");
    }
  };

  return Model;

})(HasProps);
