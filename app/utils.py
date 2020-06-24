from datetime import datetime
import jwt

def  ago(point, now=datetime.utcnow):
        mins = hrs = days = weeks = months = years = 0
        now = now()
        diff = now - point
        s = secs, suffix = diff.seconds, "secs"
        days = diff.days
        
        if secs >= 60:
                s = mins, suffix = secs // 60, "mins"
        if mins >= 60:
                s = hrs, suffix = mins // 60, "hrs"
        if days >= 1:
                s = days_, suffix = days, "days"
        if days >= 7:
                s = weeks, suffix = days // 7, "weeks"
        if weeks >= 4:
                s = months, suffix = [weeks // 4, "months"]
                if months < 12:
                        same_year = True if (now.year - point.year) == 0 else False
                        months_apart = (now.month+12) - point.month if not same_year else now.month - point.month
                        months_apart = months_apart - 1 if point.day > now.day else months_apart
                        s = [months_apart, s[1]] if months_apart else [4, "weeks"]
        if months >= 12:
                s = years, suffix = [months // 12, "years"]
                if now.month <= point.month:
                        years_apart = years - 1 if (now.month < point.month) or (now.month==point.month and now.day < point.day) else years
                        s = [years_apart, s[1]] if years_apart else [11, "months"]
        return f"{s[0]} {s[1][0:-1] if s[0] == 1 else s[1]} ago"

def ago(dt, now=datetime.utcnow):
        now = now()
        diff = now-dt
        secs = diff.seconds
        if secs < 60:
                difference, unit = secs, "second"
        elif secs < 60*60:
                difference, unit = secs // 60, "minute"
        elif secs < 60*60*24:
                difference, unit = secs // 60 // 60, "hour"
        if diff.days == 1:
                return "Yesterday"
        elif diff.days > 1 and diff.days < 7:
                difference, unit = diff.days, "day"
        elif diff.days >= 7 and diff.days < 365:
                return dt.strftime("%B %d")
        elif diff.days >= 365:
                return dt.strftime("%B %d, %Y") 
        return f"{difference} {unit if difference == 1 else unit+'s'} ago"

