import re
import yaml
import sys
import subprocess

def sanitize_name(name):
    new_name = re.sub(r'[^a-zA-Z0-9.]','-', name).lower().replace(" ", "-")
    if re.search(r'[.-0-9]$', new_name):
        return new_name + 'e'
    else:
        return new_name

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <argument>")
        sys.exit(1)

    file_path = sys.argv[1]
    with open(file_path, 'r') as file:
        multiple = yaml.safe_load_all(file)

        for data in multiple:    
            data['apiVersion'] = "maestro.ai4quantum.com/v1alpha1"
            if 'metadata' in data and 'name' in data['metadata']:
                data['metadata']['name'] = sanitize_name(data['metadata']['name'])
            if data['kind'] == "Workflow":
                # remove template.meatdata
                if data['spec']['template'].get('metadata'):
                    del data['spec']['template']['metadata']
                if data['spec']['template'].get('agents'):
                    agents = data['spec']['template']['agents']
                    samitized_agents = []
                    for agent in agents:
                        samitized_agents.append(sanitize_name(agent))
                    data['spec']['template']['agents'] = samitized_agents 
                if data['spec']['template'].get('steps'):
                    steps = data['spec']['template']['steps']
                    for step in steps:
                        if step.get('agent'):
                            step['agent'] = sanitize_name(step['agent'])
                        if step.get('parallel'):
                            agents = step['parallel']
                            samitized_agents = []
                            for agent in agents:
                                samitized_agents.append(sanitize_name(agent))
                            step['parallel'] = samitized_agents 
                if data['spec']['template'].get('exception'):
                    exception = data['spec']['template']['exception']
                    if exception.get('agent'):
                        exception['agent'] = sanitize_name(exception['agent'])
            with open("temp_yaml", 'w') as file:
                yaml.safe_dump(data, file)
                print(yaml.dump(data))
                result = subprocess.run(['kubectl', 'apply', "-f", "temp_yaml"], capture_output=True, text=True)
                print(result)
            

if __name__ == "__main__":
    main()
