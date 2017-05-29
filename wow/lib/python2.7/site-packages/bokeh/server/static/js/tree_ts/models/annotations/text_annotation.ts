var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Annotation,
  AnnotationView
} from "./annotation";

import {
  show,
  hide
} from "core/dom";

import * as p from "core/properties";

import {
  isString,
  isArray
} from "core/util/types";

import {
  get_text_height
} from "core/util/text";

export var TextAnnotationView = (function(superClass) {
  extend(TextAnnotationView, superClass);

  function TextAnnotationView() {
    return TextAnnotationView.__super__.constructor.apply(this, arguments);
  }

  TextAnnotationView.prototype.initialize = function(options) {
    TextAnnotationView.__super__.initialize.call(this, options);
    this.canvas = this.plot_model.canvas;
    this.frame = this.plot_model.frame;
    if (this.model.render_mode === 'css') {
      this.el.classList.add('bk-annotation');
      return this.plot_view.canvas_overlays.appendChild(this.el);
    }
  };

  TextAnnotationView.prototype.bind_bokeh_events = function() {
    if (this.model.render_mode === 'css') {
      return this.listenTo(this.model, 'change', this.render);
    } else {
      return this.listenTo(this.model, 'change', this.plot_view.request_render);
    }
  };

  TextAnnotationView.prototype._calculate_text_dimensions = function(ctx, text) {
    var height, width;
    width = ctx.measureText(text).width;
    height = get_text_height(this.visuals.text.font_value()).height;
    return [width, height];
  };

  TextAnnotationView.prototype._calculate_bounding_box_dimensions = function(ctx, text) {
    var height, ref, width, x_offset, y_offset;
    ref = this._calculate_text_dimensions(ctx, text), width = ref[0], height = ref[1];
    switch (ctx.textAlign) {
      case 'left':
        x_offset = 0;
        break;
      case 'center':
        x_offset = -width / 2;
        break;
      case 'right':
        x_offset = -width;
    }
    switch (ctx.textBaseline) {
      case 'top':
        y_offset = 0.0;
        break;
      case 'middle':
        y_offset = -0.5 * height;
        break;
      case 'bottom':
        y_offset = -1.0 * height;
        break;
      case 'alphabetic':
        y_offset = -0.8 * height;
        break;
      case 'hanging':
        y_offset = -0.17 * height;
        break;
      case 'ideographic':
        y_offset = -0.83 * height;
    }
    return [x_offset, y_offset, width, height];
  };

  TextAnnotationView.prototype._get_size = function() {
    var ctx;
    ctx = this.plot_view.canvas_view.ctx;
    this.visuals.text.set_value(ctx);
    return ctx.measureText(this.model.text).ascent;
  };

  TextAnnotationView.prototype.render = function() {
    return null;
  };

  TextAnnotationView.prototype._canvas_text = function(ctx, text, sx, sy, angle) {
    var bbox_dims;
    this.visuals.text.set_value(ctx);
    bbox_dims = this._calculate_bounding_box_dimensions(ctx, text);
    ctx.save();
    ctx.beginPath();
    ctx.translate(sx, sy);
    if (angle) {
      ctx.rotate(angle);
    }
    ctx.rect(bbox_dims[0], bbox_dims[1], bbox_dims[2], bbox_dims[3]);
    if (this.visuals.background_fill.doit) {
      this.visuals.background_fill.set_value(ctx);
      ctx.fill();
    }
    if (this.visuals.border_line.doit) {
      this.visuals.border_line.set_value(ctx);
      ctx.stroke();
    }
    if (this.visuals.text.doit) {
      this.visuals.text.set_value(ctx);
      ctx.fillText(text, 0, 0);
    }
    return ctx.restore();
  };

  TextAnnotationView.prototype._css_text = function(ctx, text, sx, sy, angle) {
    var bbox_dims, ld, line_dash;
    hide(this.el);
    this.visuals.text.set_value(ctx);
    bbox_dims = this._calculate_bounding_box_dimensions(ctx, text);
    ld = this.visuals.border_line.line_dash.value();
    if (isArray(ld)) {
      if (ld.length < 2) {
        line_dash = "solid";
      } else {
        line_dash = "dashed";
      }
    }
    if (isString(ld)) {
      line_dash = ld;
    }
    this.visuals.border_line.set_value(ctx);
    this.visuals.background_fill.set_value(ctx);
    this.el.style.position = 'absolute';
    this.el.style.left = (sx + bbox_dims[0]) + "px";
    this.el.style.top = (sy + bbox_dims[1]) + "px";
    this.el.style.color = "" + (this.visuals.text.text_color.value());
    this.el.style.opacity = "" + (this.visuals.text.text_alpha.value());
    this.el.style.font = "" + (this.visuals.text.font_value());
    this.el.style.lineHeight = "normal";
    if (angle) {
      this.el.style.transform = "rotate(" + angle + "rad)";
    }
    if (this.visuals.background_fill.doit) {
      this.el.style.backgroundColor = "" + (this.visuals.background_fill.color_value());
    }
    if (this.visuals.border_line.doit) {
      this.el.style.borderStyle = "" + line_dash;
      this.el.style.borderWidth = (this.visuals.border_line.line_width.value()) + "px";
      this.el.style.borderColor = "" + (this.visuals.border_line.color_value());
    }
    this.el.textContent = text;
    return show(this.el);
  };

  return TextAnnotationView;

})(AnnotationView);

export var TextAnnotation = (function(superClass) {
  extend(TextAnnotation, superClass);

  function TextAnnotation() {
    return TextAnnotation.__super__.constructor.apply(this, arguments);
  }

  TextAnnotation.prototype.type = 'TextAnnotation';

  TextAnnotation.prototype.default_view = TextAnnotationView;

  return TextAnnotation;

})(Annotation);
