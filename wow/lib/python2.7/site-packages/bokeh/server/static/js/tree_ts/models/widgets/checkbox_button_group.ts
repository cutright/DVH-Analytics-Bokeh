var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty,
  indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

import * as $ from "jquery";

import "bootstrap/button";

import {
  Widget,
  WidgetView
} from "./widget";

import {
  BokehView
} from "core/bokeh_view";

import * as p from "core/properties";

import template from "./button_group_template";

export var CheckboxButtonGroupView = (function(superClass) {
  extend(CheckboxButtonGroupView, superClass);

  function CheckboxButtonGroupView() {
    return CheckboxButtonGroupView.__super__.constructor.apply(this, arguments);
  }

  CheckboxButtonGroupView.prototype.events = {
    "change input": "change_input"
  };

  CheckboxButtonGroupView.prototype.template = template;

  CheckboxButtonGroupView.prototype.initialize = function(options) {
    CheckboxButtonGroupView.__super__.initialize.call(this, options);
    this.render();
    return this.listenTo(this.model, 'change', this.render);
  };

  CheckboxButtonGroupView.prototype.render = function() {
    var $input, $label, active, html, i, j, label, len, ref;
    CheckboxButtonGroupView.__super__.render.call(this);
    this.$el.empty();
    html = this.template();
    this.el.appendChild(html);
    active = this.model.active;
    ref = this.model.labels;
    for (i = j = 0, len = ref.length; j < len; i = ++j) {
      label = ref[i];
      $input = $('<input type="checkbox">').attr({
        value: "" + i
      });
      if (indexOf.call(active, i) >= 0) {
        $input.prop("checked", true);
      }
      $label = $('<label class="bk-bs-btn"></label>');
      $label.text(label).prepend($input);
      $label.addClass("bk-bs-btn-" + this.model.button_type);
      if (indexOf.call(active, i) >= 0) {
        $label.addClass("bk-bs-active");
      }
      this.$el.find('.bk-bs-btn-group').append($label);
    }
    return this;
  };

  CheckboxButtonGroupView.prototype.change_input = function() {
    var active, checkbox, i, ref;
    active = (function() {
      var j, len, ref, results;
      ref = this.$el.find("input");
      results = [];
      for (i = j = 0, len = ref.length; j < len; i = ++j) {
        checkbox = ref[i];
        if (checkbox.checked) {
          results.push(i);
        }
      }
      return results;
    }).call(this);
    this.model.active = active;
    return (ref = this.model.callback) != null ? ref.execute(this.model) : void 0;
  };

  return CheckboxButtonGroupView;

})(WidgetView);

export var CheckboxButtonGroup = (function(superClass) {
  extend(CheckboxButtonGroup, superClass);

  function CheckboxButtonGroup() {
    return CheckboxButtonGroup.__super__.constructor.apply(this, arguments);
  }

  CheckboxButtonGroup.prototype.type = "CheckboxButtonGroup";

  CheckboxButtonGroup.prototype.default_view = CheckboxButtonGroupView;

  CheckboxButtonGroup.define({
    active: [p.Array, []],
    labels: [p.Array, []],
    button_type: [p.String, "default"],
    callback: [p.Instance]
  });

  return CheckboxButtonGroup;

})(Widget);
