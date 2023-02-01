from core.services.coreservices import CoreService, ServiceMode


class BWMService(CoreService):
    name: str = "bwm-ng"
    group: str = "Logging"
    executables: tuple[str, ...]  = ('bwm-ng', )
    dependencies: tuple[str, ...] = ()
    dirs: tuple[str, ...] = ()
    configs: tuple[str, ...] = ()
    startup: tuple[str, ...]  = ('bash -c "nohup bwm-ng --timeout=1000 --unit=bytes --type=rate --output=csv -F bwm.csv &> bwm_run.log &"', )
    validate: tuple[str, ...]  = ('bash -c "ps -C bwm-ng"', )
    validation_mode: ServiceMode = ServiceMode.NON_BLOCKING
    validation_timer: int = 1
    validation_period: float = 1
    shutdown: tuple[str, ...] = ('bash -c "kill -INT `pgrep bwm-ng`"', )
