import subprocess
import os

class ServiceManager:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.services = self.load_services()

    def load_services(self):
        services_config = self.config_manager.get('services', {})
        return {service_name: {'config': config, 'status': 'stopped', 'process': None}
                for service_name, config in services_config.items()}

    def get_service_status(self, service_name):
        service = self.services.get(service_name)
        if not service:
            return 'not_found'

        process = service.get('process')
        if process and process.poll() is None:
            service['status'] = 'running'
        else:
            service['status'] = 'stopped'
        return service['status']


    def get_all_statuses(self):
        return {service_name: self.get_service_status(service_name)
                for service_name in self.services}

    def start_service(self, service_name):
        service = self.services.get(service_name)
        if not service or self.get_service_status(service_name) == 'running':
            return False

        config = service['config']
        command = config.get('start_command')
        if not command:
            return False

        # Using os.setsid to create a new process session.
        # This allows us to kill the entire process group later.
        process = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
        service['process'] = process
        service['status'] = 'running'
        return True

    def stop_service(self, service_name):
        service = self.services.get(service_name)
        if not service or self.get_service_status(service_name) == 'stopped':
            return False

        process = service.get('process')
        if process:
            # Killing the entire process group.
            os.killpg(os.getpgid(process.pid), 9)
            service['process'] = None
        service['status'] = 'stopped'
        return True