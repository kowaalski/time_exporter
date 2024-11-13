from prometheus_client import start_http_server, Gauge, CollectorRegistry
from datetime import datetime, timezone, timedelta
import pytz
import time

def get_local_hour_and_offset(timezones):
    """
    Returns a dictionary with the timezone as the key and a tuple of the local hour and UTC offset as the value.
    
    :param timezones: List of timezone strings (e.g., ['Europe/Madrid', 'Europe/London'])
    :return: Dictionary with timezone names as keys and tuples (local hour, UTC offset) as values.
    """
    local_hours_offsets = {}
    utc_now = datetime.now(timezone.utc)  # Get the current time in UTC as a timezone-aware datetime object
    
    for tz_name in timezones:
        tz = pytz.timezone(tz_name)
        local_time = utc_now.astimezone(tz)
        utc_offset = local_time.utcoffset()
        utc_offset_total_seconds = utc_offset.total_seconds()
        # Format UTC offset as "+HH" or "-HH" (e.g., "+02" or "-03")
        utc_offset_str = f"UTC{ utc_offset_total_seconds // 3600:+03.0f}"
        local_hours_offsets[tz_name] = (local_time.hour, utc_offset_str,  utc_offset_total_seconds / 3600)
    
    return local_hours_offsets

if __name__ == '__main__':
    # Create a new registry to avoid using the default global registry (which collects default metrics)
    registry = CollectorRegistry(auto_describe=False)
    
    # List of all timezones available in pytz
    timezones = pytz.all_timezones
    
    # Create a Gauge metric for the local hour with only the 'timezone' label
    local_hour_gauge = Gauge('local_hour', 
                             'Current local hour in the specified timezone, automatically adjusted for daylight saving time (summer/winter).',
                             ['timezone'], 
                             registry=registry)
    
    # Create another Gauge metric for UTC offset with 'timezone' and 'utc_offset' labels, and the offset as the value
    utc_offset_gauge = Gauge('timezone_utc_offset', 
                             'Current UTC offset in the specified timezone, formatted as "UTC+HH" or "UTC-HH".',
                             ['timezone', 'utc_offset'], 
                             registry=registry)

    # Start the Prometheus HTTP server on port 8000
    start_http_server(8000, registry=registry)

    print(r"""
 ___________________________________________________________________________
/\                                                                          \
\_|  _____ _                      _____                       _             |
  | |_   _(_)_ __ ___   ___      | ____|_  ___ __   ___  _ __| |_ ___ _ __  |
  |   | | | | '_ ` _ \ / _ \_____|  _| \ \/ / '_ \ / _ \| '__| __/ _ \ '__| |
  |   | | | | | | | | |  __/_____| |___ >  <| |_) | (_) | |  | ||  __/ |    |
  |   |_| |_|_| |_| |_|\___|     |_____/_/\_\ .__/ \___/|_|   \__\___|_|    |
  |                                         |_|                             |
  |   ______________________________________________________________________|_
   \_/________________________________________________________________________/
""")
    print(f"Running the time exporter for {len(timezones)} timezones. Open http://localhost:8000/ in your browser to see the metrics.")

    # Update the gauges with the local hour and UTC offset every minute
    while True:
        local_hours_offsets = get_local_hour_and_offset(timezones)
        
        # Update the local hour metric for each timezone
        for tz_name, (local_hour, utc_offset_str, utc_offset_value) in local_hours_offsets.items():
            local_hour_gauge.labels(timezone=tz_name).set(local_hour)
            
            # Set the UTC offset gauge to the numeric value of the UTC offset
            utc_offset_gauge.labels(timezone=tz_name, utc_offset=utc_offset_str).set(utc_offset_value)

        time.sleep(60)  # Update every 60 seconds
