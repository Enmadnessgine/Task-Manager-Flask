from datetime import datetime, timedelta

def hours_left(time_start: str, duration: int) -> float:
    time_format = '%H:%M:%S'
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    start_dt = datetime.strptime(f"{today_str} {time_start}", '%Y-%m-%d %H:%M:%S')
    finish_dt = start_dt + timedelta(hours=duration)
    delta = finish_dt - now
    hours_remaining = delta.total_seconds() / 3600
    return hours_remaining

