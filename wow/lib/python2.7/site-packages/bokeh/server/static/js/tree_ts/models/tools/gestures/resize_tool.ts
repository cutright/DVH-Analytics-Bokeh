var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  GestureTool,
  GestureToolView
} from "./gesture_tool";

import {
  show,
  hide
} from "core/dom";

import * as p from "core/properties";

export var ResizeToolView = (function(superClass) {
  extend(ResizeToolView, superClass);

  function ResizeToolView() {
    return ResizeToolView.__super__.constructor.apply(this, arguments);
  }

  ResizeToolView.prototype.className = "bk-resize-popup";

  ResizeToolView.prototype.initialize = function(options) {
    var wrapper;
    ResizeToolView.__super__.initialize.call(this, options);
    wrapper = this.plot_view.el.querySelector('div.bk-canvas-wrapper');
    wrapper.appendChild(this.el);
    hide(this.el);
    this.active = false;
    return null;
  };

  ResizeToolView.prototype.activate = function() {
    this.active = true;
    this.render();
    return null;
  };

  ResizeToolView.prototype.deactivate = function() {
    this.active = false;
    this.render();
    return null;
  };

  ResizeToolView.prototype.render = function(ctx) {
    var canvas, frame, left, top;
    if (this.active) {
      canvas = this.plot_view.canvas;
      frame = this.plot_view.frame;
      left = canvas.vx_to_sx(frame.h_range.end - 40);
      top = canvas.vy_to_sy(frame.v_range.start + 40);
      this.el.style.position = "absolute";
      this.el.style.top = top + "px";
      this.el.style.left = left + "px";
      show(this.el);
    } else {
      hide(this.el);
    }
    return this;
  };

  ResizeToolView.prototype._pan_start = function(e) {
    var canvas;
    canvas = this.plot_view.canvas;
    this.ch = canvas.height;
    this.cw = canvas.width;
    this.plot_view.interactive_timestamp = Date.now();
    return null;
  };

  ResizeToolView.prototype._pan = function(e) {
    this._update(e.deltaX, e.deltaY);
    this.plot_view.interactive_timestamp = Date.now();
    return null;
  };

  ResizeToolView.prototype._pan_end = function(e) {
    return this.plot_view.push_state("resize", {
      dimensions: {
        width: this.plot_view.canvas.width,
        height: this.plot_view.canvas.height
      }
    });
  };

  ResizeToolView.prototype._update = function(dx, dy) {
    var new_height, new_width;
    new_width = this.cw + dx;
    new_height = this.ch + dy;
    if (new_width < 100 || new_height < 100) {
      return;
    }
    this.plot_view.update_dimensions(new_width, new_height);
  };

  return ResizeToolView;

})(GestureToolView);

export var ResizeTool = (function(superClass) {
  extend(ResizeTool, superClass);

  function ResizeTool() {
    return ResizeTool.__super__.constructor.apply(this, arguments);
  }

  ResizeTool.prototype.default_view = ResizeToolView;

  ResizeTool.prototype.type = "ResizeTool";

  ResizeTool.prototype.tool_name = "Resize";

  ResizeTool.prototype.icon = "bk-tool-icon-resize";

  ResizeTool.prototype.event_type = "pan";

  ResizeTool.prototype.default_order = 40;

  return ResizeTool;

})(GestureTool);
