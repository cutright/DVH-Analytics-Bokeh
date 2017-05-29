var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import "jquery-ui/slider";

import {
  logger
} from "core/logging";

import * as p from "core/properties";

import {
  throttle
} from "core/util/callback";

import {
  InputWidget,
  InputWidgetView
} from "./input_widget";

import slidertemplate from "./slidertemplate";

export var RangeSliderView = (function(superClass) {
  extend(RangeSliderView, superClass);

  function RangeSliderView() {
    this.slide = bind(this.slide, this);
    this.slidestop = bind(this.slidestop, this);
    return RangeSliderView.__super__.constructor.apply(this, arguments);
  }

  RangeSliderView.prototype.template = slidertemplate;

  RangeSliderView.prototype.initialize = function(options) {
    var html;
    RangeSliderView.__super__.initialize.call(this, options);
    this.listenTo(this.model, 'change', this.render);
    this.$el.empty();
    html = this.template(this.model.attributes);
    this.$el.html(html);
    this.callbackWrapper = null;
    if (this.model.callback_policy === 'continuous') {
      this.callbackWrapper = function() {
        var ref;
        return (ref = this.model.callback) != null ? ref.execute(this.model) : void 0;
      };
    }
    if (this.model.callback_policy === 'throttle' && this.model.callback) {
      this.callbackWrapper = throttle(function() {
        var ref;
        return (ref = this.model.callback) != null ? ref.execute(this.model) : void 0;
      }, this.model.callback_throttle);
    }
    return this.render();
  };

  RangeSliderView.prototype.render = function() {
    var bk_handle, max, min, opts, step;
    RangeSliderView.__super__.render.call(this);
    max = this.model.end;
    min = this.model.start;
    step = this.model.step || ((max - min) / 50);
    logger.debug("range-slider render: min, max, step = (" + min + ", " + max + ", " + step + ")");
    opts = {
      range: true,
      orientation: this.model.orientation,
      animate: "fast",
      values: this.model.range,
      min: min,
      max: max,
      step: step,
      stop: this.slidestop,
      slide: this.slide
    };
    this.$el.find('.slider').slider(opts);
    if (this.model.title != null) {
      this.$el.find("#" + this.model.id).val(this.$el.find('.slider').slider('values').join(' - '));
    }
    this.$el.find('.bk-slider-parent').height(this.model.height);
    bk_handle = this.$el.find('.bk-ui-slider-handle');
    if (bk_handle.length === 2) {
      bk_handle[0].style.left = this.$el.find('.ui-slider-handle')[0].style.left;
      bk_handle[1].style.left = this.$el.find('.ui-slider-handle')[1].style.left;
    }
    this._prefix_ui();
    return this;
  };

  RangeSliderView.prototype.slidestop = function(event, ui) {
    var ref;
    if (this.model.callback_policy === 'mouseup' || this.model.callback_policy === 'throttle') {
      return (ref = this.model.callback) != null ? ref.execute(this.model) : void 0;
    }
  };

  RangeSliderView.prototype.slide = function(event, ui) {
    var values, values_str;
    values = ui.values;
    values_str = values.join(' - ');
    logger.debug("range-slide value = " + values_str);
    if (this.model.title != null) {
      this.$el.find("#" + this.model.id).val(values_str);
    }
    this.model.range = values;
    if (this.callbackWrapper) {
      return this.callbackWrapper();
    }
  };

  return RangeSliderView;

})(InputWidgetView);

export var RangeSlider = (function(superClass) {
  extend(RangeSlider, superClass);

  function RangeSlider() {
    return RangeSlider.__super__.constructor.apply(this, arguments);
  }

  RangeSlider.prototype.type = "RangeSlider";

  RangeSlider.prototype.default_view = RangeSliderView;

  RangeSlider.define({
    range: [p.Any, [0.1, 0.9]],
    start: [p.Number, 0],
    end: [p.Number, 1],
    step: [p.Number, 0.1],
    orientation: [p.Orientation, "horizontal"],
    callback_throttle: [p.Number, 200],
    callback_policy: [p.String, "throttle"]
  });

  return RangeSlider;

})(InputWidget);
