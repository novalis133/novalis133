import json
import re
import sys
import urllib.parse
import logging
import os

# Set up logging for GitHub Actions
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_default_metrics():
    """Create a default project_metrics.json if invalid or empty."""
    default_data = {
        "projects": [
            {
                "name": "Smart Vision Systems",
                "gain": 98,
                "color": "blue",
                "labelColor": "1976D2"
            },
            {
                "name": "Multi-Agent DRL",
                "gain": 88,
                "color": "yellow",
                "labelColor": "FFB300"
            },
            {
                "name": "Accent Analyzer",
                "gain": 92,
                "color": "red",
                "labelColor": "D32F2F"
            },
            {
                "name": "Neuron Models",
                "gain": 85,
                "color": "purple",
                "labelColor": "6A1B9A"
            }
        ]
    }
    with open('project_metrics.json', 'w') as f:
        json.dump(default_data, f, indent=2)
    logging.info("Created default project_metrics.json")
    return default_data

def validate_project_metrics(data):
    """Validate project_metrics.json structure and content."""
    if 'projects' not in data or not isinstance(data['projects'], list):
        logging.error("Invalid project_metrics.json: 'projects' key missing or not a list")
        return False
    
    required_fields = ['name', 'gain', 'color', 'labelColor']
    valid_colors = ['green', 'blue', 'yellow', 'red', 'purple', 'orange', 'grey', 'black']
    for project in data['projects']:
        for field in required_fields:
            if field not in project:
                logging.error(f"Invalid project_metrics.json: Missing '{field}' in project {project.get('name', 'unknown')}")
                return False
        if not isinstance(project['gain'], (int, float)) or project['gain'] < 0 or project['gain'] > 100:
            logging.error(f"Invalid project_metrics.json: Invalid 'gain' in project {project['name']}")
            return False
        if project['color'].lower() not in valid_colors:
            logging.warning(f"Invalid color '{project['color']}' in project {project['name']}; using 'blue'")
            project['color'] = 'blue'
        if not re.match(r'^[0-9A-Fa-f]{6}$', project['labelColor']):
            logging.warning(f"Invalid labelColor '{project['labelColor']}' in project {project['name']}; using '000000'")
            project['labelColor'] = '000000'
    return True

def generate_badge(project):
    """Generate badge markdown for a project."""
    name = urllib.parse.quote(project['name'].replace(' ', '_'))  # Sanitize for URL
    gain = project['gain']
    color = project['color'].lower()
    label_color = project['labelColor']
    badge_url = f"https://img.shields.io/badge/{name}-{gain}%25-{color}?labelColor={label_color}"
    return f"| {project['name']} | ![{project['name']} Gain]({badge_url}) |"

try:
    # Check if project_metrics.json exists and is not empty
    if not os.path.exists('project_metrics.json'):
        logging.warning("project_metrics.json is missing; creating default")
        data = create_default_metrics()
    elif os.path.getsize('project_metrics.json') == 0:
        logging.warning("project_metrics.json is empty; creating default")
        data = create_default_metrics()
    else:
        with open('project_metrics.json', 'r') as f:
            raw_content = f.read()
            if not raw_content.strip():
                logging.warning("project_metrics.json contains only whitespace; creating default")
                data = create_default_metrics()
            else:
                data = json.loads(raw_content)
    
    # Validate project metrics
    if not validate_project_metrics(data):
        logging.warning("Invalid project_metrics.json; using default")
        data = create_default_metrics()

    # Generate badge markdown
    badges = [generate_badge(project) for project in data['projects']]
    new_table = "\n".join(badges)
    logging.info("Generated badge table:\n%s", new_table)

    # Read README
    with open('README.md', 'r') as f:
        content = f.read()

    # Update badge table
    pattern = r'(\| Project\s+\|\s+Performance Gain\s+\|\n\|[-]+\|\s*[-]+\|\n)(.*?)(?=\n\n[A-Z#])'
    if not re.search(pattern, content, re.DOTALL):
        logging.error("Could not find Project Impact Dashboard table in README.md")
        sys.exit(1)
    
    new_content = re.sub(pattern, f"\g<1>{new_table}\n", content, flags=re.DOTALL)
    
    # Write updated README
    with open('README.md', 'w') as f:
        f.write(new_content)
    logging.info("Successfully updated README.md with new badges")

except FileNotFoundError as e:
    logging.error("File not found: %s", e)
    sys.exit(1)
except json.JSONDecodeError as e:
    logging.error("Invalid JSON in project_metrics.json: %s", e)
    try:
        with open('project_metrics.json', 'r') as f:
            raw_content = f.read()
        logging.debug("Raw content of project_metrics.json:\n%s", raw_content if raw_content else "File is empty")
    except Exception as debug_e:
        logging.debug("Could not read project_metrics.json for debugging: %s", debug_e)
    logging.warning("Using default project_metrics.json")
    data = create_default_metrics()
    badges = [generate_badge(project) for project in data['projects']]
    new_table = "\n".join(badges)
    with open('README.md', 'r') as f:
        content = f.read()
    new_content = re.sub(pattern, f"\g<1>{new_table}\n", content, flags=re.DOTALL)
    with open('README.md', 'w') as f:
        f.write(new_content)
    logging.info("Successfully updated README.md with default badges")
except Exception as e:
    logging.error("Unexpected error: %s", e)
    sys.exit(1)