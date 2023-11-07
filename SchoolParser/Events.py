from datetime import datetime, timedelta


class Events:
    def get_datetime_start_event(self, start_date, notify: bool = False) -> str:
        date_string = start_date
        date_format = '%Y-%m-%dT%H:%M:%SZ'
        start_datetime = datetime.strptime(date_string, date_format) + timedelta(hours=7)
        current_datetime = datetime.now()
        time_difference = start_datetime - current_datetime

        if time_difference.total_seconds() < 1: return False

        if time_difference.total_seconds() > 1800 and notify: return False

        res_days = time_difference.days
        res_hours = time_difference.seconds // 3600
        res_minutes = (time_difference.seconds % 3600) // 60

        minutes_str = self.pluralize(res_minutes, ('минута', 'минуты', 'минут'))

        if res_days == 0 and res_hours == 0:
            return f'{res_minutes} {minutes_str}.'

        days_str = self.pluralize(res_days, ('день', 'дня', 'дней'))
        hours_str = self.pluralize(res_hours, ('час', 'часа', 'часов'))

        return f'{res_days} {days_str}, {res_hours} {hours_str} и {res_minutes} {minutes_str}.'

    def pluralize(self, n, forms):
        if n % 10 == 1 and n % 100 != 11:
            return forms[0]
        elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
            return forms[1]
        else:
            return forms[2]

    def get_from_to_date(self, type: str = 'from') -> str:
        current_datetime = datetime.now()
        from_date = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        if type == 'to':
            to_date = (current_datetime + timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            return to_date

        return from_date
