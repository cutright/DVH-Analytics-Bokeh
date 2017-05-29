var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Annotation
} from "./annotation";

import {
  Visuals
} from "core/visuals";

import * as p from "core/properties";

export var ArrowHead = (function(superClass) {
  extend(ArrowHead, superClass);

  function ArrowHead() {
    return ArrowHead.__super__.constructor.apply(this, arguments);
  }

  ArrowHead.prototype.type = 'ArrowHead';

  ArrowHead.prototype.initialize = function(options) {
    ArrowHead.__super__.initialize.call(this, options);
    return this.visuals = new Visuals(this);
  };

  ArrowHead.prototype.render = function(ctx, i) {
    return null;
  };

  ArrowHead.prototype.clip = function(ctx, i) {
    return null;
  };

  return ArrowHead;

})(Annotation);

export var OpenHead = (function(superClass) {
  extend(OpenHead, superClass);

  function OpenHead() {
    return OpenHead.__super__.constructor.apply(this, arguments);
  }

  OpenHead.prototype.type = 'OpenHead';

  OpenHead.prototype.clip = function(ctx, i) {
    this.visuals.line.set_vectorize(ctx, i);
    ctx.moveTo(0.5 * this.size, this.size);
    ctx.lineTo(0.5 * this.size, -2);
    ctx.lineTo(-0.5 * this.size, -2);
    ctx.lineTo(-0.5 * this.size, this.size);
    ctx.lineTo(0, 0);
    return ctx.lineTo(0.5 * this.size, this.size);
  };

  OpenHead.prototype.render = function(ctx, i) {
    if (this.visuals.line.doit) {
      this.visuals.line.set_vectorize(ctx, i);
      ctx.beginPath();
      ctx.moveTo(0.5 * this.size, this.size);
      ctx.lineTo(0, 0);
      ctx.lineTo(-0.5 * this.size, this.size);
      return ctx.stroke();
    }
  };

  OpenHead.mixins(['line']);

  OpenHead.define({
    size: [p.Number, 25]
  });

  return OpenHead;

})(ArrowHead);

export var NormalHead = (function(superClass) {
  extend(NormalHead, superClass);

  function NormalHead() {
    return NormalHead.__super__.constructor.apply(this, arguments);
  }

  NormalHead.prototype.type = 'NormalHead';

  NormalHead.prototype.clip = function(ctx, i) {
    this.visuals.line.set_vectorize(ctx, i);
    ctx.moveTo(0.5 * this.size, this.size);
    ctx.lineTo(0.5 * this.size, -2);
    ctx.lineTo(-0.5 * this.size, -2);
    ctx.lineTo(-0.5 * this.size, this.size);
    return ctx.lineTo(0.5 * this.size, this.size);
  };

  NormalHead.prototype.render = function(ctx, i) {
    if (this.visuals.fill.doit) {
      this.visuals.fill.set_vectorize(ctx, i);
      this._normal(ctx, i);
      ctx.fill();
    }
    if (this.visuals.line.doit) {
      this.visuals.line.set_vectorize(ctx, i);
      this._normal(ctx, i);
      return ctx.stroke();
    }
  };

  NormalHead.prototype._normal = function(ctx, i) {
    ctx.beginPath();
    ctx.moveTo(0.5 * this.size, this.size);
    ctx.lineTo(0, 0);
    ctx.lineTo(-0.5 * this.size, this.size);
    return ctx.closePath();
  };

  NormalHead.mixins(['line', 'fill']);

  NormalHead.define({
    size: [p.Number, 25]
  });

  NormalHead.override({
    fill_color: 'black'
  });

  return NormalHead;

})(ArrowHead);

export var VeeHead = (function(superClass) {
  extend(VeeHead, superClass);

  function VeeHead() {
    return VeeHead.__super__.constructor.apply(this, arguments);
  }

  VeeHead.prototype.type = 'VeeHead';

  VeeHead.prototype.clip = function(ctx, i) {
    this.visuals.line.set_vectorize(ctx, i);
    ctx.moveTo(0.5 * this.size, this.size);
    ctx.lineTo(0.5 * this.size, -2);
    ctx.lineTo(-0.5 * this.size, -2);
    ctx.lineTo(-0.5 * this.size, this.size);
    ctx.lineTo(0, 0.5 * this.size);
    return ctx.lineTo(0.5 * this.size, this.size);
  };

  VeeHead.prototype.render = function(ctx, i) {
    if (this.visuals.fill.doit) {
      this.visuals.fill.set_vectorize(ctx, i);
      this._vee(ctx, i);
      ctx.fill();
    }
    if (this.visuals.line.doit) {
      this.visuals.line.set_vectorize(ctx, i);
      this._vee(ctx, i);
      return ctx.stroke();
    }
  };

  VeeHead.prototype._vee = function(ctx, i) {
    ctx.beginPath();
    ctx.moveTo(0.5 * this.size, this.size);
    ctx.lineTo(0, 0);
    ctx.lineTo(-0.5 * this.size, this.size);
    ctx.lineTo(0, 0.5 * this.size);
    return ctx.closePath();
  };

  VeeHead.mixins(['line', 'fill']);

  VeeHead.define({
    size: [p.Number, 25]
  });

  VeeHead.override({
    fill_color: 'black'
  });

  return VeeHead;

})(ArrowHead);
