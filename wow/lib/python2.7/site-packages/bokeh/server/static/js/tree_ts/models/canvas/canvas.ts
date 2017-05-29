var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import canvas_template from "./canvas_template";

import {
  LayoutCanvas
} from "core/layout/layout_canvas";

import {
  BokehView
} from "core/bokeh_view";

import {
  GE,
  EQ
} from "core/layout/solver";

import {
  logger
} from "core/logging";

import * as p from "core/properties";

import {
  isEqual
} from "core/util/eq";

import {
  fixup_image_smoothing,
  fixup_line_dash,
  fixup_line_dash_offset,
  fixup_measure_text,
  get_scale_ratio,
  fixup_ellipse
} from "core/util/canvas";

export var CanvasView = (function(superClass) {
  extend(CanvasView, superClass);

  function CanvasView() {
    return CanvasView.__super__.constructor.apply(this, arguments);
  }

  CanvasView.prototype.className = "bk-canvas-wrapper";

  CanvasView.prototype.template = canvas_template;

  CanvasView.prototype.initialize = function(options) {
    var html;
    CanvasView.__super__.initialize.call(this, options);
    html = this.template({
      map: this.model.map
    });
    this.el.appendChild(html);
    this.ctx = this.get_ctx();
    fixup_line_dash(this.ctx);
    fixup_line_dash_offset(this.ctx);
    fixup_image_smoothing(this.ctx);
    fixup_measure_text(this.ctx);
    fixup_ellipse(this.ctx);
    if (window.CanvasPixelArray != null) {
      CanvasPixelArray.prototype.set = function(arr) {
        var i, j, ref, results;
        results = [];
        for (i = j = 0, ref = this.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
          results.push(this[i] = arr[i]);
        }
        return results;
      };
    }
    this.map_div = this.el.querySelector('div.bk-canvas-map');
    this.set_dims([this.model.initial_width, this.model.initial_height]);
    return logger.debug("CanvasView initialized");
  };

  CanvasView.prototype.get_canvas_element = function() {
    return this.el.querySelector('canvas.bk-canvas');
  };

  CanvasView.prototype.get_ctx = function() {
    return this.get_canvas_element().getContext('2d');
  };

  CanvasView.prototype.prepare_canvas = function(force) {
    var canvas_el, dpr, height, ratio, width;
    if (force == null) {
      force = false;
    }
    width = this.model._width._value;
    height = this.model._height._value;
    dpr = window.devicePixelRatio;
    if (!isEqual(this.last_dims, [width, height, dpr]) || force) {
      this.el.style.width = width + "px";
      this.el.style.height = height + "px";
      this.pixel_ratio = ratio = get_scale_ratio(this.ctx, this.model.use_hidpi);
      canvas_el = this.get_canvas_element();
      canvas_el.style.width = width + "px";
      canvas_el.style.height = height + "px";
      canvas_el.setAttribute('width', width * ratio);
      canvas_el.setAttribute('height', height * ratio);
      logger.debug("Rendering CanvasView [force=" + force + "] with width: " + width + ", height: " + height + ", ratio: " + ratio);
      this.model.pixel_ratio = this.pixel_ratio;
      return this.last_dims = [width, height, dpr];
    }
  };

  CanvasView.prototype.set_dims = function(dims, trigger) {
    if (trigger == null) {
      trigger = true;
    }
    this.requested_width = dims[0];
    this.requested_height = dims[1];
    this.update_constraints(trigger);
  };

  CanvasView.prototype.update_constraints = function(trigger) {
    var MIN_SIZE, requested_height, requested_width, s;
    if (trigger == null) {
      trigger = true;
    }
    requested_width = this.requested_width;
    requested_height = this.requested_height;
    if ((requested_width == null) || (requested_height == null)) {
      return;
    }
    MIN_SIZE = 50;
    if (requested_width < MIN_SIZE || requested_height < MIN_SIZE) {
      return;
    }
    if (isEqual(this.last_requested_dims, [requested_width, requested_height])) {
      return;
    }
    s = this.model.document.solver();
    if (this._width_constraint != null) {
      s.remove_constraint(this._width_constraint, true);
    }
    this._width_constraint = EQ(this.model._width, -requested_width);
    s.add_constraint(this._width_constraint);
    if (this._height_constraint != null) {
      s.remove_constraint(this._height_constraint, true);
    }
    this._height_constraint = EQ(this.model._height, -requested_height);
    s.add_constraint(this._height_constraint);
    this.last_requested_dims = [requested_width, requested_height];
    return s.update_variables(trigger);
  };

  return CanvasView;

})(BokehView);

export var Canvas = (function(superClass) {
  extend(Canvas, superClass);

  function Canvas() {
    return Canvas.__super__.constructor.apply(this, arguments);
  }

  Canvas.prototype.type = 'Canvas';

  Canvas.prototype.default_view = CanvasView;

  Canvas.internal({
    map: [p.Boolean, false],
    initial_width: [p.Number],
    initial_height: [p.Number],
    use_hidpi: [p.Boolean, true],
    pixel_ratio: [p.Number]
  });

  Canvas.prototype.initialize = function(attrs, options) {
    Canvas.__super__.initialize.call(this, attrs, options);
    return this.panel = this;
  };

  Canvas.prototype.vx_to_sx = function(x) {
    return x;
  };

  Canvas.prototype.vy_to_sy = function(y) {
    return this._height._value - (y + 1);
  };

  Canvas.prototype.v_vx_to_sx = function(xx) {
    return new Float64Array(xx);
  };

  Canvas.prototype.v_vy_to_sy = function(yy) {
    var _yy, height, idx, j, len, y;
    _yy = new Float64Array(yy.length);
    height = this._height._value;
    for (idx = j = 0, len = yy.length; j < len; idx = ++j) {
      y = yy[idx];
      _yy[idx] = height - (y + 1);
    }
    return _yy;
  };

  Canvas.prototype.sx_to_vx = function(x) {
    return x;
  };

  Canvas.prototype.sy_to_vy = function(y) {
    return this._height._value - (y + 1);
  };

  Canvas.prototype.v_sx_to_vx = function(xx) {
    return new Float64Array(xx);
  };

  Canvas.prototype.v_sy_to_vy = function(yy) {
    var _yy, height, idx, j, len, y;
    _yy = new Float64Array(yy.length);
    height = this._height._value;
    for (idx = j = 0, len = yy.length; j < len; idx = ++j) {
      y = yy[idx];
      _yy[idx] = height - (y + 1);
    }
    return _yy;
  };

  Canvas.prototype.get_constraints = function() {
    var constraints;
    constraints = Canvas.__super__.get_constraints.call(this);
    constraints.push(GE(this._top));
    constraints.push(GE(this._bottom));
    constraints.push(GE(this._left));
    constraints.push(GE(this._right));
    constraints.push(GE(this._width));
    constraints.push(GE(this._height));
    constraints.push(EQ(this._width, [-1, this._right]));
    constraints.push(EQ(this._height, [-1, this._top]));
    return constraints;
  };

  return Canvas;

})(LayoutCanvas);
