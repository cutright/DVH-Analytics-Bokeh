var delegateEventSplitter;

import * as $ from "jquery";

import {
  isFunction
} from "core/util/types";

delegateEventSplitter = /^(\S+)\s*(.*)$/;

export var JQueryable = {
  _prefix_ui: function() {
    var classList, cls, el, i, j, len, len1, ref, ref1;
    ref = this.el.querySelectorAll("*[class*='ui-']");
    for (i = 0, len = ref.length; i < len; i++) {
      el = ref[i];
      classList = [];
      ref1 = el.classList;
      for (j = 0, len1 = ref1.length; j < len1; j++) {
        cls = ref1[j];
        classList.push(cls.indexOf("ui-") === 0 ? "bk-" + cls : cls);
      }
      el.className = classList.join(" ");
    }
    return null;
  },
  _setElement: function(el) {
    this.$el = el instanceof $ ? el : $(el);
    return this.el = this.$el[0];
  },
  setElement: function(element) {
    this.undelegateEvents();
    this._setElement(element);
    this.delegateEvents();
    return this;
  },
  delegateEvents: function(events) {
    var key, match, method;
    if (events == null) {
      events = this.events;
    }
    if (!events) {
      return this;
    }
    this.undelegateEvents();
    for (key in events) {
      method = events[key];
      if (!isFunction(method)) {
        method = this[method];
      }
      if (method == null) {
        continue;
      }
      match = key.match(delegateEventSplitter);
      this.delegate(match[1], match[2], method.bind(this));
    }
    return this;
  },
  delegate: function(eventName, selector, listener) {
    this.$el.on(eventName + '.delegateEvents' + this.id, selector, listener);
    return this;
  },
  undelegateEvents: function() {
    if (this.$el) {
      this.$el.off('.delegateEvents' + this.id);
    }
    return this;
  },
  undelegate: function(eventName, selector, listener) {
    this.$el.off(eventName + '.delegateEvents' + this.id, selector, listener);
    return this;
  }
};
