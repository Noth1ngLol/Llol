import json
import os

def validate_gguf_file(file_path):
    # Implement GGUF file validation logic here
    # For now, we'll just check if the file exists and has a .gguf extension
    return os.path.exists(file_path) and file_path.lower().endswith('.gguf')

def load_default_config():
    return {
        "metadata_to_modify": [
            {
                "key": "model_name",
                "value": "My Custom Model",
                "type": "string"
            },
            {
                "key": "num_layers",
                "value": 32,
                "type": "int"
            }
        ],
        "metadata_to_add": [
            {
                "key": "custom_parameter",
                "value": 0.75,
                "type": "float"
            }
        ],
        "metadata_to_remove": [
            "unused_parameter"
        ],
        "comments": {
            "model_name": "Set your custom model name (string)",
            "num_layers": "Number of layers in the model (integer)",
            "custom_parameter": "A custom parameter value (float between 0 and 1)",
            "unused_parameter": "This parameter will be removed from the metadata"
        }
    }

def save_config(config_path, config):
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Add comments to the file
    with open(config_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    commented_lines = []
    for line in lines:
        commented_lines.append(line)
        if '"key":' in line:
            key = line.split('"')[3]
            if key in config['comments']:
                commented_lines.append(f"    // {config['comments'][key]}")
    
    with open(config_path, 'w') as f:
        f.write('\n'.join(commented_lines))
