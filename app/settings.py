import os
import yaml
from pathlib import Path
from .logger import appLogger

logger = appLogger(__name__)


def get_param(config, param, default=None):
    try:
        config_param = config[param]
    except Exception:
        config_param = default if default else None
    finally:
        logger.debug(f"{param}: {config_param}")
        return config_param

class Required:
    def __init__(self, v_type=None):
        self.v_type = v_type


class Settings:

    statuses = {
        'OK': 0,
        'ERR_TIMED_OUT': 1,
        'ERR_STRING_NOT_FOUND': 2,
        'ERR_STATUS_CODE': 3,
        'ERR_OTHER': 4,
        'ERR_STRING_CODE': 5,
    }
    """
    Any setting defined here can be overridden by:

    Settings the appropriate environment variable, eg. to override FOOBAR, `export APP_FOOBAR="whatever"`.
    This is useful in production for secrets you do not wish to save in code and
    also plays nicely with docker(-compose). Settings will attempt to convert environment variables to match the
    type of the value here. See also activate.settings.sh.

    Or, passing the custom setting as a keyword argument when initialising settings (useful when testing)
    """
    _ENV_PREFIX = 'APP_'
    # you should replace this with another value via the environment variable APP_COOKIE_SECRET
    # which is not saved in code, you could also use Required(str) to force the env variable to be set.
    COOKIE_SECRET = 'uyq5aSB8H9lmZW_ZMa0SZtbQQQTDerpU8f-1Zne7KYQ='

    conf_file = None
    proxy = None
    timeout = None
    frequency = None
    trigger_threshold = None
    recover_threshold = None
    alarm_repeat = None
    services = None
    resources = None
    loglevel = None

    def __init__(self, **custom_settings):
        """
        :param custom_settings: Custom settings to override defaults, only attributes already defined can be set.
        """
        self._custom_settings = custom_settings
        self.substitute_environ()
        for name, value in custom_settings.items():
            if not hasattr(self, name):
                raise TypeError('{} is not a valid setting name'.format(name))
            setattr(self, name, value)
        self.load()

    def substitute_environ(self):
        """
        Substitute environment variables into settings.
        """
        for attr_name in dir(self):
            if attr_name.startswith('_') or attr_name.upper() != attr_name:
                continue

            orig_value = getattr(self, attr_name)
            is_required = isinstance(orig_value, Required)
            orig_type = orig_value.v_type if is_required else type(orig_value)
            env_var_name = self._ENV_PREFIX + attr_name
            env_var = os.getenv(env_var_name, None)
            if env_var is not None:
                if issubclass(orig_type, bool):
                    env_var = env_var.upper() in ('1', 'TRUE')
                elif issubclass(orig_type, int):
                    env_var = int(env_var)
                elif issubclass(orig_type, Path):
                    env_var = Path(env_var)
                elif issubclass(orig_type, bytes):
                    env_var = env_var.encode()
                # could do floats here and lists etc via json
                setattr(self, attr_name, env_var)
            elif is_required and attr_name not in self._custom_settings:
                raise RuntimeError('The required environment variable "{0}" is currently not set, '
                                   'you\'ll need to run `source activate.settings.sh` '
                                   'or you can set that single environment variable with '
                                   '`export {0}="<value>"`'.format(env_var_name))

    # @staticmethod
    def load(self):
        self.conf_file = os.environ.get('CONFIG_FILE', 'config.yaml')
        try:
            with open(self.conf_file, 'r') as stream:
                config = yaml.load(stream)
        except Exception as e:
            logger.error(f"Unable to read config from file: {self.conf_file} {e}")
            config = dict()

        self.proxy = get_param(config, 'proxy')
        self.timeout = get_param(config, 'timeout', 10)
        self.frequency = get_param(config, 'frequency', 15)
        self.trigger_threshold = get_param(config, 'trigger_threshold', 2)
        self.recover_threshold = get_param(config, 'recover_threshold', 3)
        self.alarm_repeat = get_param(config, 'alarm_repeat', 300)
        self.frequency = get_param(config, 'frequency', 15)
        self.services = get_param(config, 'services')
        self.resources = get_param(config, 'resources')

    # @staticmethod
    def get_enabled_services(self):
        return list(self.services.keys()) if self.services else {}

    @property
    def enabled_services(self):
        return list(self.services.keys()) if self.services else {}

    def get_status_name(self, code):
        for key, val in self.statuses.items():
            if code == val:
                return key
