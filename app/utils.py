from datetime import datetime
import jwt
import os

def  dir_last_updated(folder):
        return str(max(os.path.getmtime(os.path.join(root_path, f))
                        for root_path, dirs, files in os.walk(folder)
                        for f in files))


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

