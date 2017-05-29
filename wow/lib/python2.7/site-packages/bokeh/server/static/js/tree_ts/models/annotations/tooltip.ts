var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Annotation,
  AnnotationView
} from "./annotation";

import {
  logger
} from "core/logging";

import {
  div,
  show,
  hide,
  empty
} from "core/dom";

import * as p from "core/properties";

export var TooltipView = (function(superClass) {
  extend(TooltipView, superClass);

  function TooltipView() {
    return TooltipView.__super__.constructor.apply(this, arguments);
  }

  TooltipView.prototype.className = "bk-tooltip";

  TooltipView.prototype.initialize = function(options) {
    TooltipView.__super__.initialize.call(this, options);
    this.plot_view.canvas_overlays.appendChild(this.el);
    this.el.style.zIndex = 1010;
    return hide(this.el);
  };

  TooltipView.prototype.bind_bokeh_events = function() {
    return this.listenTo(this.model, 'change:data', this._draw_tips);
  };

  TooltipView.prototype.render = function() {
    if (!this.model.visible) {
      return;
    }
    return this._draw_tips();
  };

  TooltipView.prototype._draw_tips = function() {
    var arrow_size, attachment, bottom, content, data, height, i, left, len, side, sx, sy, tip, top, val, vx, vy, width;
    data = this.model.data;
    empty(this.el);
    hide(this.el);
    if (this.model.custom) {
      this.el.classList.add("bk-tooltip-custom");
    } else {
      this.el.classList.remove("bk-tooltip-custom");
    }
    if (data.length === 0) {
      return;
    }
    for (i = 0, len = data.length; i < len; i++) {
      val = data[i];
      vx = val[0], vy = val[1], content = val[2];
      if (this.model.inner_only && !this.plot_view.frame.contains(vx, vy)) {
        continue;
      }
      tip = div({}, content);
      this.el.appendChild(tip);
    }
    sx = this.plot_view.model.canvas.vx_to_sx(vx);
    sy = this.plot_view.model.canvas.vy_to_sy(vy);
    attachment = this.model.attachment;
    switch (attachment) {
      case "horizontal":
        width = this.plot_view.frame.width;
        left = this.plot_view.frame.left;
        if (vx - left < width / 2) {
          side = 'right';
        } else {
          side = 'left';
        }
        break;
      case "vertical":
        height = this.plot_view.frame.height;
        bottom = this.plot_view.frame.bottom;
        if (vy - bottom < height / 2) {
          side = 'below';
        } else {
          side = 'above';
        }
        break;
      default:
        side = attachment;
    }
    this.el.classList.remove("bk-right");
    this.el.classList.remove("bk-left");
    this.el.classList.remove("bk-above");
    this.el.classList.remove("bk-below");
    arrow_size = 10;
    show(this.el);
    switch (side) {
      case "right":
        this.el.classList.add("bk-left");
        left = sx + (this.el.offsetWidth - this.el.clientWidth) + arrow_size;
        top = sy - this.el.offsetHeight / 2;
        break;
      case "left":
        this.el.classList.add("bk-right");
        left = sx - this.el.offsetWidth - arrow_size;
        top = sy - this.el.offsetHeight / 2;
        break;
      case "above":
        this.el.classList.add("bk-above");
        top = sy + (this.el.offsetHeight - this.el.clientHeight) + arrow_size;
        left = Math.round(sx - this.el.offsetWidth / 2);
        break;
      case "below":
        this.el.classList.add("bk-below");
        top = sy - this.el.offsetHeight - arrow_size;
        left = Math.round(sx - this.el.offsetWidth / 2);
    }
    if (this.model.show_arrow) {
      this.el.classList.add("bk-tooltip-arrow");
    }
    if (this.el.childNodes.length > 0) {
      this.el.style.top = top + "px";
      return this.el.style.left = left + "px";
    } else {
      return hide(this.el);
    }
  };

  return TooltipView;

})(AnnotationView);

export var Tooltip = (function(superClass) {
  extend(Tooltip, superClass);

  function Tooltip() {
    return Tooltip.__super__.constructor.apply(this, arguments);
  }

  Tooltip.prototype.default_view = TooltipView;

  Tooltip.prototype.type = 'Tooltip';

  Tooltip.define({
    attachment: [p.String, 'horizontal'],
    inner_only: [p.Bool, true],
    show_arrow: [p.Bool, true]
  });

  Tooltip.override({
    level: 'overlay'
  });

  Tooltip.internal({
    data: [p.Any, []],
    custom: [p.Any]
  });

  Tooltip.prototype.clear = function() {
    return this.data = [];
  };

  Tooltip.prototype.add = function(vx, vy, content) {
    var data;
    data = this.data;
    data.push([vx, vy, content]);
    this.data = data;
    return this.trigger('change:data');
  };

  return Tooltip;

})(Annotation);
