import * as object from "./core/util/object";

import * as array from "./core/util/array";

import * as string from "./core/util/string";

import * as types from "./core/util/types";

import * as eq from "./core/util/eq";

export var LinAlg = object.extend({}, object, array, string, types, eq);

import * as Charts from "./api/charts";

export {
  Charts
};

import * as Plotting from "./api/plotting";

export {
  Plotting
};

export {
  Document
} from "./document";

import * as sprintf from "sprintf";

export {
  sprintf
};

export * from "./api/models";
