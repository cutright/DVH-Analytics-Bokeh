var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  ActionTool,
  ActionToolView
} from "./action_tool";

export var SaveToolView = (function(superClass) {
  extend(SaveToolView, superClass);

  function SaveToolView() {
    return SaveToolView.__super__.constructor.apply(this, arguments);
  }

  SaveToolView.prototype["do"] = function() {
    return this.plot_view.save("bokeh_plot.png");
  };

  return SaveToolView;

})(ActionToolView);

export var SaveTool = (function(superClass) {
  extend(SaveTool, superClass);

  function SaveTool() {
    return SaveTool.__super__.constructor.apply(this, arguments);
  }

  SaveTool.prototype.default_view = SaveToolView;

  SaveTool.prototype.type = "SaveTool";

  SaveTool.prototype.tool_name = "Save";

  SaveTool.prototype.icon = "bk-tool-icon-save";

  return SaveTool;

})(ActionTool);
