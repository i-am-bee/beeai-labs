import sys
import yaml
import json
import jsonschema

def validate_yaml(yaml_file, schema_file):
    with open(schema_file, 'r') as f:
        schema = json.load(f)
        print(schema)

    with open(yaml_file, 'r') as f:
        yamls = yaml.safe_load_all(f)
        for yaml_data in yamls:
            json_data = json.dumps(yaml_data, indent=4)
            print(json_data)
            jsonschema.validate(yaml_data, schema)
            print("YAML file is valid.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate.py yamlfile schemafile")
    else:
        validate_yaml(sys.argv[1], sys.argv[2])
