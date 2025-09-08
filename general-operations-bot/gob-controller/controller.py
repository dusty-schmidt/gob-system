import time
from config_manager import ConfigManager
from service_manager import ServiceManager
from health_monitor import HealthMonitor

class GOBController:
    def __init__(self):
        self.config_manager = ConfigManager(config_path='/home/ds/sambashare/GOB/GOB-system/config/gob.yaml')
        self.service_manager = ServiceManager(self.config_manager)
        self.health_monitor = HealthMonitor(self.service_manager)

    def run(self):
        print("GOB Controller Started")
        
        print("\n--- Starting all services ---")
        for service in self.service_manager.services:
            if service != 'gob-controller':
                self.service_manager.start_service(service)
        
        time.sleep(5) # Give the services some time to start

        print("\n--- System Health ---")
        print(self.health_monitor.get_system_health())

    def stop_all_services(self):
        print("\n--- Stopping all services ---")
        for service in self.service_manager.services:
            if service != 'gob-controller':
                self.service_manager.stop_service(service)
        print(self.health_monitor.get_system_health())


if __name__ == '__main__':
    controller = GOBController()
    try:
        controller.run()
        # Keep the controller running for a while to monitor the services.
        # In a real application, this would be an event loop or a server.
        time.sleep(10)
    finally:
        controller.stop_all_services()
