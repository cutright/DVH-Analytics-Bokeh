var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  ButtonTool,
  ButtonToolView
} from "../button_tool";

export var GestureToolView = (function(superClass) {
  extend(GestureToolView, superClass);

  function GestureToolView() {
    return GestureToolView.__super__.constructor.apply(this, arguments);
  }

  return GestureToolView;

})(ButtonToolView);

export var GestureTool = (function(superClass) {
  extend(GestureTool, superClass);

  function GestureTool() {
    return GestureTool.__super__.constructor.apply(this, arguments);
  }

  GestureTool.prototype.event_type = null;

  GestureTool.prototype.default_order = null;

  return GestureTool;

})(ButtonTool);
