var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Annotation,
  AnnotationView
} from "./annotation";

import * as p from "core/properties";

import {
  get_text_height
} from "core/util/text";

import {
  BBox
} from "core/util/bbox";

import {
  max,
  all
} from "core/util/array";

import {
  values
} from "core/util/object";

import {
  isString,
  isArray
} from "core/util/types";

export var LegendView = (function(superClass) {
  extend(LegendView, superClass);

  function LegendView() {
    return LegendView.__super__.constructor.apply(this, arguments);
  }

  LegendView.prototype.initialize = function(options) {
    return LegendView.__super__.initialize.call(this, options);
  };

  LegendView.prototype.bind_bokeh_events = function() {
    return this.listenTo(this.model, 'change:visible', this.plot_view.request_render);
  };

  LegendView.prototype.compute_legend_bbox = function() {
    var ctx, glyph_height, glyph_width, h_range, i, label_height, label_standoff, label_width, legend_height, legend_margin, legend_names, legend_padding, legend_spacing, legend_width, len, location, max_label_width, name, panel, ref, ref1, v_range, width, x, y;
    legend_names = this.model.get_legend_names();
    glyph_height = this.model.glyph_height;
    glyph_width = this.model.glyph_width;
    label_height = this.model.label_height;
    label_width = this.model.label_width;
    this.max_label_height = max([get_text_height(this.visuals.label_text.font_value()).height, label_height, glyph_height]);
    ctx = this.plot_view.canvas_view.ctx;
    ctx.save();
    this.visuals.label_text.set_value(ctx);
    this.text_widths = {};
    for (i = 0, len = legend_names.length; i < len; i++) {
      name = legend_names[i];
      this.text_widths[name] = max([ctx.measureText(name).width, label_width]);
    }
    ctx.restore();
    max_label_width = max(values(this.text_widths));
    legend_margin = this.model.margin;
    legend_padding = this.model.padding;
    legend_spacing = this.model.spacing;
    label_standoff = this.model.label_standoff;
    if (this.model.orientation === "vertical") {
      legend_height = legend_names.length * this.max_label_height + (legend_names.length - 1) * legend_spacing + 2 * legend_padding;
      legend_width = max_label_width + glyph_width + label_standoff + 2 * legend_padding;
    } else {
      legend_width = 2 * legend_padding + (legend_names.length - 1) * legend_spacing;
      ref = this.text_widths;
      for (name in ref) {
        width = ref[name];
        legend_width += max([width, label_width]) + glyph_width + label_standoff;
      }
      legend_height = this.max_label_height + 2 * legend_padding;
    }
    panel = (ref1 = this.model.panel) != null ? ref1 : this.plot_view.frame;
    h_range = {
      start: panel.left,
      end: panel.right
    };
    v_range = {
      start: panel.bottom,
      end: panel.top
    };
    location = this.model.location;
    if (isString(location)) {
      switch (location) {
        case 'top_left':
          x = h_range.start + legend_margin;
          y = v_range.end - legend_margin;
          break;
        case 'top_center':
          x = (h_range.end + h_range.start) / 2 - legend_width / 2;
          y = v_range.end - legend_margin;
          break;
        case 'top_right':
          x = h_range.end - legend_margin - legend_width;
          y = v_range.end - legend_margin;
          break;
        case 'center_right':
          x = h_range.end - legend_margin - legend_width;
          y = (v_range.end + v_range.start) / 2 + legend_height / 2;
          break;
        case 'bottom_right':
          x = h_range.end - legend_margin - legend_width;
          y = v_range.start + legend_margin + legend_height;
          break;
        case 'bottom_center':
          x = (h_range.end + h_range.start) / 2 - legend_width / 2;
          y = v_range.start + legend_margin + legend_height;
          break;
        case 'bottom_left':
          x = h_range.start + legend_margin;
          y = v_range.start + legend_margin + legend_height;
          break;
        case 'center_left':
          x = h_range.start + legend_margin;
          y = (v_range.end + v_range.start) / 2 + legend_height / 2;
          break;
        case 'center':
          x = (h_range.end + h_range.start) / 2 - legend_width / 2;
          y = (v_range.end + v_range.start) / 2 + legend_height / 2;
      }
    } else if (isArray(location) && location.length === 2) {
      x = location[0], y = location[1];
      x += h_range.start;
      y += v_range.start + legend_height;
    }
    x = this.plot_view.canvas.vx_to_sx(x);
    y = this.plot_view.canvas.vy_to_sy(y);
    return {
      x: x,
      y: y,
      width: legend_width,
      height: legend_height
    };
  };

  LegendView.prototype.bbox = function() {
    var height, ref, width, x, y;
    ref = this.compute_legend_bbox(), x = ref.x, y = ref.y, width = ref.width, height = ref.height;
    return new BBox({
      x0: x,
      y0: y,
      x1: x + width,
      y1: y + height
    });
  };

  LegendView.prototype.on_hit = function(sx, sy) {
    var bbox, field, glyph_height, glyph_width, h, i, item, j, k, l, label, label_standoff, labels, legend_bbox, legend_spacing, len, len1, len2, len3, r, ref, ref1, ref2, ref3, ref4, vertical, w, x1, x2, xoffset, y1, y2, yoffset;
    glyph_height = this.model.glyph_height;
    glyph_width = this.model.glyph_width;
    legend_spacing = this.model.spacing;
    label_standoff = this.model.label_standoff;
    xoffset = yoffset = this.model.padding;
    legend_bbox = this.compute_legend_bbox();
    vertical = this.model.orientation === "vertical";
    ref = this.model.items;
    for (i = 0, len = ref.length; i < len; i++) {
      item = ref[i];
      labels = item.get_labels_list_from_label_prop();
      field = item.get_field_from_label_prop();
      for (j = 0, len1 = labels.length; j < len1; j++) {
        label = labels[j];
        x1 = legend_bbox.x + xoffset;
        y1 = legend_bbox.y + yoffset;
        x2 = x1 + glyph_width;
        y2 = y1 + glyph_height;
        if (vertical) {
          ref1 = [legend_bbox.width - 2 * this.model.padding, this.max_label_height], w = ref1[0], h = ref1[1];
        } else {
          ref2 = [this.text_widths[label] + glyph_width + label_standoff, this.max_label_height], w = ref2[0], h = ref2[1];
        }
        bbox = new BBox({
          x0: x1,
          y0: y1,
          x1: x1 + w,
          y1: y1 + h
        });
        if (bbox.contains(sx, sy)) {
          switch (this.model.click_policy) {
            case "hide":
              ref3 = item.renderers;
              for (k = 0, len2 = ref3.length; k < len2; k++) {
                r = ref3[k];
                r.visible = !r.visible;
              }
              break;
            case "mute":
              ref4 = item.renderers;
              for (l = 0, len3 = ref4.length; l < len3; l++) {
                r = ref4[l];
                r.muted = !r.muted;
              }
          }
          return true;
        }
        if (vertical) {
          yoffset += this.max_label_height + legend_spacing;
        } else {
          xoffset += this.text_widths[label] + glyph_width + label_standoff + legend_spacing;
        }
      }
    }
    return false;
  };

  LegendView.prototype.render = function() {
    var bbox, ctx;
    if (!this.model.visible) {
      return;
    }
    if (this.model.items.length === 0) {
      return;
    }
    ctx = this.plot_view.canvas_view.ctx;
    bbox = this.compute_legend_bbox();
    ctx.save();
    this._draw_legend_box(ctx, bbox);
    this._draw_legend_items(ctx, bbox);
    return ctx.restore();
  };

  LegendView.prototype._draw_legend_box = function(ctx, bbox) {
    ctx.beginPath();
    ctx.rect(bbox.x, bbox.y, bbox.width, bbox.height);
    this.visuals.background_fill.set_value(ctx);
    ctx.fill();
    if (this.visuals.border_line.doit) {
      this.visuals.border_line.set_value(ctx);
      return ctx.stroke();
    }
  };

  LegendView.prototype._draw_legend_items = function(ctx, bbox) {
    var active, field, glyph_height, glyph_width, h, i, item, j, k, label, label_standoff, labels, legend_spacing, len, len1, len2, r, ref, ref1, ref2, ref3, vertical, view, w, x1, x2, xoffset, y1, y2, yoffset;
    glyph_height = this.model.glyph_height;
    glyph_width = this.model.glyph_width;
    legend_spacing = this.model.spacing;
    label_standoff = this.model.label_standoff;
    xoffset = yoffset = this.model.padding;
    vertical = this.model.orientation === "vertical";
    ref = this.model.items;
    for (i = 0, len = ref.length; i < len; i++) {
      item = ref[i];
      labels = item.get_labels_list_from_label_prop();
      field = item.get_field_from_label_prop();
      if (labels.length === 0) {
        continue;
      }
      active = (function() {
        switch (this.model.click_policy) {
          case "none":
            return true;
          case "hide":
            return all(item.renderers, function(r) {
              return r.visible;
            });
          case "mute":
            return all(item.renderers, function(r) {
              return !r.muted;
            });
        }
      }).call(this);
      for (j = 0, len1 = labels.length; j < len1; j++) {
        label = labels[j];
        x1 = bbox.x + xoffset;
        y1 = bbox.y + yoffset;
        x2 = x1 + glyph_width;
        y2 = y1 + glyph_height;
        if (vertical) {
          yoffset += this.max_label_height + legend_spacing;
        } else {
          xoffset += this.text_widths[label] + glyph_width + label_standoff + legend_spacing;
        }
        this.visuals.label_text.set_value(ctx);
        ctx.fillText(label, x2 + label_standoff, y1 + this.max_label_height / 2.0);
        ref1 = item.renderers;
        for (k = 0, len2 = ref1.length; k < len2; k++) {
          r = ref1[k];
          view = this.plot_view.renderer_views[r.id];
          view.draw_legend(ctx, x1, x2, y1, y2, field, label);
        }
        if (!active) {
          if (vertical) {
            ref2 = [bbox.width - 2 * this.model.padding, this.max_label_height], w = ref2[0], h = ref2[1];
          } else {
            ref3 = [this.text_widths[label] + glyph_width + label_standoff, this.max_label_height], w = ref3[0], h = ref3[1];
          }
          ctx.beginPath();
          ctx.rect(x1, y1, w, h);
          this.visuals.inactive_fill.set_value(ctx);
          ctx.fill();
        }
      }
    }
    return null;
  };

  LegendView.prototype._get_size = function() {
    var bbox, side;
    bbox = this.compute_legend_bbox();
    side = this.model.panel.side;
    if (side === 'above' || side === 'below') {
      return bbox.height;
    }
    if (side === 'left' || side === 'right') {
      return bbox.width;
    }
  };

  return LegendView;

})(AnnotationView);

export var Legend = (function(superClass) {
  extend(Legend, superClass);

  function Legend() {
    return Legend.__super__.constructor.apply(this, arguments);
  }

  Legend.prototype.default_view = LegendView;

  Legend.prototype.type = 'Legend';

  Legend.prototype.cursor = function() {
    if (this.click_policy === "none") {
      return null;
    } else {
      return "pointer";
    }
  };

  Legend.prototype.get_legend_names = function() {
    var i, item, labels, legend_names, len, ref;
    legend_names = [];
    ref = this.items;
    for (i = 0, len = ref.length; i < len; i++) {
      item = ref[i];
      labels = item.get_labels_list_from_label_prop();
      legend_names = legend_names.concat(labels);
    }
    return legend_names;
  };

  Legend.mixins(['text:label_', 'fill:inactive_', 'line:border_', 'fill:background_']);

  Legend.define({
    orientation: [p.Orientation, 'vertical'],
    location: [p.Any, 'top_right'],
    label_standoff: [p.Number, 5],
    glyph_height: [p.Number, 20],
    glyph_width: [p.Number, 20],
    label_height: [p.Number, 20],
    label_width: [p.Number, 20],
    margin: [p.Number, 10],
    padding: [p.Number, 10],
    spacing: [p.Number, 3],
    items: [p.Array, []],
    click_policy: [p.Any, "none"]
  });

  Legend.override({
    border_line_color: "#e5e5e5",
    border_line_alpha: 0.5,
    border_line_width: 1,
    background_fill_color: "#ffffff",
    background_fill_alpha: 0.95,
    inactive_fill_color: "white",
    inactive_fill_alpha: 0.9,
    label_text_font_size: "10pt",
    label_text_baseline: "middle"
  });

  return Legend;

})(Annotation);
