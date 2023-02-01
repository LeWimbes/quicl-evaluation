from core.services.coreservices import CoreService, ServiceMode


class PidstatService(CoreService):
    name: str = "pidstat"
    group: str = "Logging"
    executables: tuple[str, ...]  = ('pidstat', )
    startup: tuple[str, ...]  = ('bash -c "nohup pidstat -drush -p ALL 1 > pidstat.log 2> pidstat_run.log &"', )
    validate: tuple[str, ...]  = ('bash -c "ps -C pidstat"', )     # ps -C returns 0 if the process is found, 1 if not.
    validation_mode: ServiceMode = ServiceMode.NON_BLOCKING  # NON_BLOCKING uses the validate commands for validation.
    validation_timer: int = 1                        # Wait 1 second before validating service.
    validation_period: float = 1                       # Retry after 1 second if validation was not successful.
    shutdown: tuple[str, ...] = ('bash -c "kill -INT `pgrep pidstat`"', )
