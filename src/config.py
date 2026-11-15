import os

DEFAULT_REFRESH_INTERVAL = 3600

TRUE_VALUES = {'1', 'true', 'yes', 'on'}
FALSE_VALUES = {'0', 'false', 'no', 'off'}


def env_flag(name, default):
    value = os.environ.get(name, '').strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False

    return default


def refresh_interval():
    try:
        return int(os.environ.get('refresh_interval', DEFAULT_REFRESH_INTERVAL))
    except ValueError:
        return DEFAULT_REFRESH_INTERVAL


def membership_only():
    return env_flag('membership', True)
