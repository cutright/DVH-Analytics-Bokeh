"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ONE_MILLI = 1.0;
exports.ONE_SECOND = 1000.0;
exports.ONE_MINUTE = 60.0 * exports.ONE_SECOND;
exports.ONE_HOUR = 60 * exports.ONE_MINUTE;
exports.ONE_DAY = 24 * exports.ONE_HOUR;
exports.ONE_MONTH = 30 * exports.ONE_DAY;
exports.ONE_YEAR = 365 * exports.ONE_DAY;
exports.copy_date = function (date) {
    return new Date(date.getTime());
};
exports.last_month_no_later_than = function (date) {
    date = exports.copy_date(date);
    date.setUTCDate(1);
    date.setUTCHours(0);
    date.setUTCMinutes(0);
    date.setUTCSeconds(0);
    date.setUTCMilliseconds(0);
    return date;
};
exports.last_year_no_later_than = function (date) {
    date = exports.last_month_no_later_than(date);
    date.setUTCMonth(0);
    return date;
};
