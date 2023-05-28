import datetime;
now = datetime.datetime.now;

class Est_Time(datetime.tzinfo):
    def dst(self, _):
        return datetime.timedelta(0)
    def utcoffset(self, _):
        return datetime.timedelta(hours = -5);
est_time = Est_Time();

def formatTime(time, bold=True):
    bold = bold and "**" or "";
    return f"{bold}{time.month}/{time.day}/{time.year}{bold} at {bold}{time.hour}:{time.minute}:{time.second}{bold}";

def timeNow(bold=True):
    return formatTime(now(), bold = bold);

def getTimeFromMessage(message, formatted=True, bold=True):
    result = message.created_at.astimezone(tz = est_time);
    if formatted:
        result = formatTime(result, bold = bold);
    return result;
