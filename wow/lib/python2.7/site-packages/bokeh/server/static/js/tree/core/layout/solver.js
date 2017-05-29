"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var _constrainer, _weak_constrainer, extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var kiwi_1 = require("kiwi");
exports.Variable = kiwi_1.Variable;
exports.Expression = kiwi_1.Expression;
exports.Constraint = kiwi_1.Constraint;
exports.Operator = kiwi_1.Operator;
exports.Strength = kiwi_1.Strength;
var events_1 = require("../events");
_constrainer = function (op) {
    return (function (_this) {
        return function () {
            var expr;
            expr = Object.create(kiwi_1.Expression.prototype);
            kiwi_1.Expression.apply(expr, arguments);
            return new kiwi_1.Constraint(expr, op);
        };
    })(this);
};
_weak_constrainer = function (op) {
    return function () {
        var arg, args, i, len;
        args = [null];
        for (i = 0, len = arguments.length; i < len; i++) {
            arg = arguments[i];
            args.push(arg);
        }
        return new kiwi_1.Constraint(new (Function.prototype.bind.apply(kiwi_1.Expression, args)), op, kiwi_1.Strength.weak);
    };
};
exports.EQ = _constrainer(kiwi_1.Operator.Eq);
exports.LE = _constrainer(kiwi_1.Operator.Le);
exports.GE = _constrainer(kiwi_1.Operator.Ge);
exports.WEAK_EQ = _weak_constrainer(kiwi_1.Operator.Eq);
exports.WEAK_LE = _weak_constrainer(kiwi_1.Operator.Le);
exports.WEAK_GE = _weak_constrainer(kiwi_1.Operator.Ge);
exports.Solver = (function () {
    extend(Solver.prototype, events_1.Events);
    function Solver() {
        this.solver = new kiwi_1.Solver();
    }
    Solver.prototype.clear = function () {
        return this.solver = new kiwi_1.Solver();
    };
    Solver.prototype.toString = function () {
        return "Solver[num_constraints=" + (this.num_constraints()) + ", num_edit_variables=" + (this.num_edit_variables()) + "]";
    };
    Solver.prototype.num_constraints = function () {
        return this.solver._cnMap._array.length;
    };
    Solver.prototype.num_edit_variables = function () {
        return this.solver._editMap._array.length;
    };
    Solver.prototype.update_variables = function (trigger) {
        if (trigger == null) {
            trigger = true;
        }
        this.solver.updateVariables();
        if (trigger) {
            return this.trigger('layout_update');
        }
    };
    Solver.prototype.add_constraint = function (constraint) {
        return this.solver.addConstraint(constraint);
    };
    Solver.prototype.remove_constraint = function (constraint, silent) {
        if (silent == null) {
            silent = false;
        }
        return this.solver.removeConstraint(constraint, silent);
    };
    Solver.prototype.add_edit_variable = function (variable, strength) {
        return this.solver.addEditVariable(variable, strength);
    };
    Solver.prototype.remove_edit_variable = function (variable, silent) {
        if (silent == null) {
            silent = false;
        }
        return this.solver.removeEditVariable(variable, strength, silent);
    };
    Solver.prototype.suggest_value = function (variable, value) {
        return this.solver.suggestValue(variable, value);
    };
    return Solver;
})();
