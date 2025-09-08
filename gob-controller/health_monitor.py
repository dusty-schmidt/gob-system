from datetime import datetime

class HealthMonitor:
    def __init__(self, service_manager):
        self.service_manager = service_manager

    def check_service(self, service_name):
        status = self.service_manager.get_service_status(service_name)
        return {
            'service': service_name,
            'status': 'healthy' if status == 'running' else 'down',
            'response_time': 0.0,  # Placeholder
            'last_check': datetime.now().isoformat(),
            'dependencies': []  # Placeholder
        }

    def get_system_health(self):
        statuses = self.service_manager.get_all_statuses()
        return {service_name: self.check_service(service_name)
                for service_name in statuses}
