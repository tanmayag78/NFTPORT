import os
import time
from logging.handlers import TimedRotatingFileHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_logging_config():
    """
    This generate logging configuration w.r.t given params which will be use in
     code base to log something as per need.

    :return: A dict containing logging conf
    """
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(process)d %(thread)d %(filename)s %(module)s %(funcName)s %(lineno)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s: %(message)s'
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'file': {
                'level': 'INFO',
                'class': 'nftport.logging.CustomTimedRotatingFileHandler',
                'filename': os.path.join(BASE_DIR, 'logs/nftport.log'),
                'formatter': 'verbose',
                'encoding': 'utf-8',
            },
        },
        'loggers': {
            'django.security.DisallowedHost': {
                'handlers': ['file'],
                'propagate': False,
            },
            '': {
                'handlers': ['file'],
                'level': 'INFO',
            },
            'django': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
            'django.db': {
                'handlers': ['file'],
                'level': 'WARNING',
                'propagate': False,
            },
        }
    }


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    def _open(self):
        """
        Make sure the mode is always 'a'
        """
        self.mode = 'a'
        return super(CustomTimedRotatingFileHandler, self)._open()

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        # get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval

        time_tuple = time.gmtime(t) if self.utc else time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, time_tuple)

        if not os.path.exists(dfn):
            os.rename(self.baseFilename, dfn)

        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

        self.mode = 'a'
        self.stream = self._open()

        current_time = int(time.time())
        new_rollover_at = self.computeRollover(current_time)

        while new_rollover_at <= current_time:
            new_rollover_at = new_rollover_at + self.interval

        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dst_now = time.localtime(current_time)[-1]
            dst_at_rollover = time.localtime(new_rollover_at)[-1]

            if dst_now != dst_at_rollover:
                if not dst_now:
                    # DST kicks in before next rollover, so we need to deduct
                    # an hour
                    new_rollover_at = new_rollover_at - 3600
                else:
                    # DST bows out before next rollover, so we need to add
                    # an hour
                    new_rollover_at = new_rollover_at + 3600

        self.rolloverAt = new_rollover_at
