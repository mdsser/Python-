import subprocess
import sys


def check_service_status(service_name):
    result = subprocess.run(['sc', 'query', service_name], capture_output=True, text=True)
    if 'RUNNING' in result.stdout:
        return 'RUNNING'
    elif 'STOPPED' in result.stdout:
        return 'STOPPED'
    else:
        return 'UNKNOWN'


def get_service_details(service_name):
    result = subprocess.run(['sc', 'qc', service_name], capture_output=True, text=True)
    return result.stdout


def start_service(service_name):
    result = subprocess.run(['net', 'start', service_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f'Service {service_name} started successfully.')
    else:
        print(f'Failed to start service {service_name}. Error: {result.stderr}')


def stop_service(service_name):
    result = subprocess.run(['net', 'stop', service_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f'Service {service_name} stopped successfully.')
    else:
        print(f'Failed to stop service {service_name}. Error: {result.stderr}')


def restart_service(service_name):
    stop_service(service_name)
    start_service(service_name)


def list_services():
    result = subprocess.run(['sc', 'queryex', 'type=', 'service', 'state=', 'all'], capture_output=True, text=True)
    services = result.stdout.split('\n')
    service_list = []
    for service in services:
        if 'SERVICE_NAME:' in service:
            service_name = service.split(':')[1].strip()
            service_list.append(service_name)
    return service_list


def main():
    if len(sys.argv) < 3:
        print("Usage: python service_manager.py <action> <service_name>")
        print("Actions: status, details, start, stop, restart, list")
        return

    action = sys.argv[1].lower()
    service_name = sys.argv[2] if len(sys.argv) > 2 else None

    if action == 'status' and service_name:
        status = check_service_status(service_name)
        print(f'Service {service_name} is {status}.')
    elif action == 'details' and service_name:
        details = get_service_details(service_name)
        print(f'Details for service {service_name}:\n{details}')
    elif action == 'start' and service_name:
        start_service(service_name)
    elif action == 'stop' and service_name:
        stop_service(service_name)
    elif action == 'restart' and service_name:
        restart_service(service_name)
    elif action == 'list':
        services = list_services()
        print("List of services:")
        for service in services:
            print(service)
    else:
        print("Invalid action or service name.")
        print("Usage: python service_manager.py <action> <service_name>")
        print("Actions: status, details, start, stop, restart, list")


if __name__ == '__main__':
    main()
