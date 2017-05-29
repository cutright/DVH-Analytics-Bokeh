var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  ActionTool,
  ActionToolView
} from "./action_tool";

import * as p from "core/properties";

export var HelpToolView = (function(superClass) {
  extend(HelpToolView, superClass);

  function HelpToolView() {
    return HelpToolView.__super__.constructor.apply(this, arguments);
  }

  HelpToolView.prototype["do"] = function() {
    return window.open(this.model.redirect);
  };

  return HelpToolView;

})(ActionToolView);

export var HelpTool = (function(superClass) {
  extend(HelpTool, superClass);

  function HelpTool() {
    return HelpTool.__super__.constructor.apply(this, arguments);
  }

  HelpTool.prototype.default_view = HelpToolView;

  HelpTool.prototype.type = "HelpTool";

  HelpTool.prototype.tool_name = "Help";

  HelpTool.prototype.icon = "bk-tool-icon-help";

  HelpTool.define({
    help_tooltip: [p.String, 'Click the question mark to learn more about Bokeh plot tools.'],
    redirect: [p.String, 'http://bokeh.pydata.org/en/latest/docs/user_guide/tools.html']
  });

  HelpTool.getters({
    tooltip: function() {
      return this.help_tooltip;
    }
  });

  return HelpTool;

})(ActionTool);
