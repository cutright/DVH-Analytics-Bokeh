export var ONE_MILLI = 1.0;

export var ONE_SECOND = 1000.0;

export var ONE_MINUTE = 60.0 * ONE_SECOND;

export var ONE_HOUR = 60 * ONE_MINUTE;

export var ONE_DAY = 24 * ONE_HOUR;

export var ONE_MONTH = 30 * ONE_DAY;

export var ONE_YEAR = 365 * ONE_DAY;

export var copy_date = function(date) {
  return new Date(date.getTime());
};

export var last_month_no_later_than = function(date) {
  date = copy_date(date);
  date.setUTCDate(1);
  date.setUTCHours(0);
  date.setUTCMinutes(0);
  date.setUTCSeconds(0);
  date.setUTCMilliseconds(0);
  return date;
};

export var last_year_no_later_than = function(date) {
  date = last_month_no_later_than(date);
  date.setUTCMonth(0);
  return date;
};
