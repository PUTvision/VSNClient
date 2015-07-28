from dbus import SystemBus, Interface


class SystemdManager:
    """
    Manage systemd services using D-Bus
    """
    def __init__(self):
        bus = SystemBus()
        systemd = bus.get_object('org.freedesktop.systemd1',
                                 '/org/freedesktop/systemd1')
        self.__systemd_manager = Interface(systemd, dbus_interface='org.freedesktop.systemd1.Manager')

    def start_service(self, service_name: str):
        """
        Start a service.
        :param service_name: name of the service to start
        """
        if service_name.endswith('.service'):
            service_name = service_name
        else:
            service_name += '.service'

        self.__systemd_manager.StartUnit(service_name, 'replace')

    def stop_service(self, service_name: str):
        """
        Stop a service.
        :param service_name: name of the service to stop
        """
        if service_name.endswith('.service'):
            service_name = service_name
        else:
            service_name += '.service'

        self.__systemd_manager.StopUnit(service_name, 'replace')

    def poweroff(self):
        """
        Switch off the device
        """
        self.__systemd_manager.PowerOff()

    def reboot(self):
        """
        Reboot the device
        """
        self.__systemd_manager.Reboot()
