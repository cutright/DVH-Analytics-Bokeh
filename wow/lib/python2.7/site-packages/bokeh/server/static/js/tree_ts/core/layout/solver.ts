var _constrainer, _weak_constrainer,
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Variable,
  Expression,
  Constraint,
  Operator,
  Strength,
  Solver as ConstraintSolver
} from "kiwi";

import {
  Events
} from "../events";

_constrainer = function(op) {
  return (function(_this) {
    return function() {
      var expr;
      expr = Object.create(Expression.prototype);
      Expression.apply(expr, arguments);
      return new Constraint(expr, op);
    };
  })(this);
};

_weak_constrainer = function(op) {
  return function() {
    var arg, args, i, len;
    args = [null];
    for (i = 0, len = arguments.length; i < len; i++) {
      arg = arguments[i];
      args.push(arg);
    }
    return new Constraint(new (Function.prototype.bind.apply(Expression, args)), op, Strength.weak);
  };
};

export {
  Variable,
  Expression,
  Constraint,
  Operator,
  Strength
};

export var EQ = _constrainer(Operator.Eq);

export var LE = _constrainer(Operator.Le);

export var GE = _constrainer(Operator.Ge);

export var WEAK_EQ = _weak_constrainer(Operator.Eq);

export var WEAK_LE = _weak_constrainer(Operator.Le);

export var WEAK_GE = _weak_constrainer(Operator.Ge);

export var Solver = (function() {
  extend(Solver.prototype, Events);

  function Solver() {
    this.solver = new ConstraintSolver();
  }

  Solver.prototype.clear = function() {
    return this.solver = new ConstraintSolver();
  };

  Solver.prototype.toString = function() {
    return "Solver[num_constraints=" + (this.num_constraints()) + ", num_edit_variables=" + (this.num_edit_variables()) + "]";
  };

  Solver.prototype.num_constraints = function() {
    return this.solver._cnMap._array.length;
  };

  Solver.prototype.num_edit_variables = function() {
    return this.solver._editMap._array.length;
  };

  Solver.prototype.update_variables = function(trigger) {
    if (trigger == null) {
      trigger = true;
    }
    this.solver.updateVariables();
    if (trigger) {
      return this.trigger('layout_update');
    }
  };

  Solver.prototype.add_constraint = function(constraint) {
    return this.solver.addConstraint(constraint);
  };

  Solver.prototype.remove_constraint = function(constraint, silent) {
    if (silent == null) {
      silent = false;
    }
    return this.solver.removeConstraint(constraint, silent);
  };

  Solver.prototype.add_edit_variable = function(variable, strength) {
    return this.solver.addEditVariable(variable, strength);
  };

  Solver.prototype.remove_edit_variable = function(variable, silent) {
    if (silent == null) {
      silent = false;
    }
    return this.solver.removeEditVariable(variable, strength, silent);
  };

  Solver.prototype.suggest_value = function(variable, value) {
    return this.solver.suggestValue(variable, value);
  };

  return Solver;

})();
