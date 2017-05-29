var extend1 = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Model
} from "../../model";

import {
  empty
} from "core/dom";

import * as p from "core/properties";

import {
  GE,
  EQ,
  Strength,
  Variable
} from "core/layout/solver";

import {
  build_views
} from "core/build_views";

import {
  BokehView
} from "core/bokeh_view";

import {
  logger
} from "core/logging";

import {
  extend
} from "core/util/object";

export var LayoutDOMView = (function(superClass) {
  extend1(LayoutDOMView, superClass);

  function LayoutDOMView() {
    return LayoutDOMView.__super__.constructor.apply(this, arguments);
  }

  LayoutDOMView.prototype.initialize = function(options) {
    var cls, i, len, ref;
    LayoutDOMView.__super__.initialize.call(this, options);
    this.el.setAttribute("id", "modelid_" + this.model.id);
    this.el.classList.add("bk-layout-" + this.model.sizing_mode);
    if (this.model.css_classes != null) {
      ref = this.model.css_classes;
      for (i = 0, len = ref.length; i < len; i++) {
        cls = ref[i];
        this.el.classList.add(cls);
      }
    }
    this.child_views = {};
    return this.build_child_views(false);
  };

  LayoutDOMView.prototype.build_child_views = function(init_solver) {
    var child, child_view, children, i, len;
    if (init_solver == null) {
      init_solver = true;
    }
    this.unbind_bokeh_events();
    if (init_solver) {
      this.model.document._invalidate_all_models();
      this.model.document._init_solver();
    }
    children = this.model.get_layoutable_children();
    this.child_views = {};
    build_views(this.child_views, children);
    empty(this.el);
    for (i = 0, len = children.length; i < len; i++) {
      child = children[i];
      child_view = this.child_views[child.id];
      this.el.appendChild(child_view.el);
    }
    return this.bind_bokeh_events();
  };

  LayoutDOMView.prototype.unbind_bokeh_events = function() {
    var id, ref, results, view;
    this.stopListening();
    ref = this.child_views;
    results = [];
    for (id in ref) {
      view = ref[id];
      view.stopListening();
      results.push(typeof view.unbind_bokeh_events === "function" ? view.unbind_bokeh_events() : void 0);
    }
    return results;
  };

  LayoutDOMView.prototype.bind_bokeh_events = function() {
    var sizing_mode_msg;
    this.listenTo(this.model, 'change', this.render);
    if (this.model.sizing_mode === 'fixed') {
      this.listenToOnce(this.model.document.solver(), 'resize', (function(_this) {
        return function() {
          return _this.render();
        };
      })(this));
    } else {
      this.listenTo(this.model.document.solver(), 'resize', (function(_this) {
        return function() {
          return _this.render();
        };
      })(this));
    }
    sizing_mode_msg = "Changing sizing_mode after initialization is not currently supported.";
    return this.listenTo(this.model, 'change:sizing_mode', function() {
      return logger.warn(sizing_mode_msg);
    });
  };

  LayoutDOMView.prototype.render = function() {
    var height, s, width;
    s = this.model.document.solver();
    if (this.model.sizing_mode === 'fixed') {
      if (this.model.width != null) {
        width = this.model.width;
      } else {
        width = this.get_width();
        this.model.width = width;
      }
      if (this.model.height != null) {
        height = this.model.height;
      } else {
        height = this.get_height();
        this.model.height = height;
      }
      s.suggest_value(this.model._width, width);
      s.suggest_value(this.model._height, height);
      s.update_variables();
      this.el.style.width = width + "px";
      this.el.style.height = height + "px";
    }
    if (this.model.sizing_mode === 'scale_width') {
      height = this.get_height();
      s.suggest_value(this.model._height, height);
      s.update_variables();
      this.el.style.width = this.model._width._value + "px";
      this.el.style.height = this.model._height._value + "px";
    }
    if (this.model.sizing_mode === 'scale_height') {
      width = this.get_width();
      s.suggest_value(this.model._width, width);
      s.update_variables();
      this.el.style.width = this.model._width._value + "px";
      this.el.style.height = this.model._height._value + "px";
    }
    if (this.model.sizing_mode === 'stretch_both') {
      this.el.style.position = 'absolute';
      this.el.style.left = this.model._dom_left._value + "px";
      this.el.style.top = this.model._dom_top._value + "px";
      this.el.style.width = this.model._width._value + "px";
      return this.el.style.height = this.model._height._value + "px";
    }
  };

  LayoutDOMView.prototype.get_height = function() {
    return null;
  };

  LayoutDOMView.prototype.get_width = function() {
    return null;
  };

  return LayoutDOMView;

})(BokehView);

export var LayoutDOM = (function(superClass) {
  extend1(LayoutDOM, superClass);

  function LayoutDOM() {
    return LayoutDOM.__super__.constructor.apply(this, arguments);
  }

  LayoutDOM.prototype.type = "LayoutDOM";

  LayoutDOM.prototype.initialize = function(attrs, options) {
    LayoutDOM.__super__.initialize.call(this, attrs, options);
    this._width = new Variable("_width " + this.id);
    this._height = new Variable("_height " + this.id);
    this._left = new Variable("_left " + this.id);
    this._right = new Variable("_right " + this.id);
    this._top = new Variable("_top " + this.id);
    this._bottom = new Variable("_bottom " + this.id);
    this._dom_top = new Variable("_dom_top " + this.id);
    this._dom_left = new Variable("_dom_left " + this.id);
    this._width_minus_right = new Variable("_width_minus_right " + this.id);
    this._height_minus_bottom = new Variable("_height_minus_bottom " + this.id);
    this._whitespace_top = new Variable();
    this._whitespace_bottom = new Variable();
    this._whitespace_left = new Variable();
    return this._whitespace_right = new Variable();
  };

  LayoutDOM.prototype.get_constraints = function() {
    var constraints;
    constraints = [];
    constraints.push(GE(this._dom_left));
    constraints.push(GE(this._dom_top));
    constraints.push(GE(this._left));
    constraints.push(GE(this._width, [-1, this._right]));
    constraints.push(GE(this._top));
    constraints.push(GE(this._height, [-1, this._bottom]));
    constraints.push(EQ(this._width_minus_right, [-1, this._width], this._right));
    constraints.push(EQ(this._height_minus_bottom, [-1, this._height], this._bottom));
    return constraints;
  };

  LayoutDOM.prototype.get_layoutable_children = function() {
    return [];
  };

  LayoutDOM.prototype.get_edit_variables = function() {
    var edit_variables;
    edit_variables = [];
    if (this.sizing_mode === 'fixed') {
      edit_variables.push({
        edit_variable: this._height,
        strength: Strength.strong
      });
      edit_variables.push({
        edit_variable: this._width,
        strength: Strength.strong
      });
    }
    if (this.sizing_mode === 'scale_width') {
      edit_variables.push({
        edit_variable: this._height,
        strength: Strength.strong
      });
    }
    if (this.sizing_mode === 'scale_height') {
      edit_variables.push({
        edit_variable: this._width,
        strength: Strength.strong
      });
    }
    return edit_variables;
  };

  LayoutDOM.prototype.get_constrained_variables = function() {
    var constrained_variables;
    constrained_variables = {
      'origin-x': this._dom_left,
      'origin-y': this._dom_top,
      'whitespace-top': this._whitespace_top,
      'whitespace-bottom': this._whitespace_bottom,
      'whitespace-left': this._whitespace_left,
      'whitespace-right': this._whitespace_right
    };
    if (this.sizing_mode === 'stretch_both') {
      constrained_variables = extend(constrained_variables, {
        'width': this._width,
        'height': this._height
      });
    }
    if (this.sizing_mode === 'scale_width') {
      constrained_variables = extend(constrained_variables, {
        'width': this._width
      });
    }
    if (this.sizing_mode === 'scale_height') {
      constrained_variables = extend(constrained_variables, {
        'height': this._height
      });
    }
    return constrained_variables;
  };

  LayoutDOM.define({
    height: [p.Number],
    width: [p.Number],
    disabled: [p.Bool, false],
    sizing_mode: [p.SizingMode, "fixed"],
    css_classes: [p.Array]
  });

  LayoutDOM.internal({
    layoutable: [p.Bool, true]
  });

  return LayoutDOM;

})(Model);
