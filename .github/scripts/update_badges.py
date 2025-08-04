
import json
import re
import sys
import urllib.parse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_project_metrics(data):
    """Validate project_metrics.json structure."""
    if 'projects' not in data or not isinstance(data['projects'], list):
        logging.error("Invalid project_metrics.json: 'projects' key missing or not a list")
        sys.exit(1)
    
    required_fields = ['name', 'gain', 'color', 'labelColor']
    for project in data['projects']:
        for field in required_fields:
            if field not in project:
                logging.error(f"Invalid project_metrics.json: Missing '{field}' in project {project.get('name', 'unknown')}")
                sys.exit(1)
        if not isinstance(project['gain'], (int, float)) or project['gain'] < 0:
            logging.error(f"Invalid project_metrics.json: Invalid 'gain' in project {project['name']}")
            sys.exit(1)

def generate_badge(project):
    """Generate badge markdown for a project."""
    name = urllib.parse.quote(project['name'].replace(' ', '_'))  # Sanitize for URL
    gain = project['gain']
    color = project['color']
    label_color = project['labelColor']
    badge_url = f"https://img.shields.io/badge/{name}-{gain}%25-{color}?labelColor={label_color}"
    return f"| {project['name']} | ![{project['name']} Gain]({badge_url}) |"

try:
    # Read project metrics
    with open('project_metrics.json', 'r') as f:
        data = json.load(f)
    
    # Validate project metrics
    validate_project_metrics(data)

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
    sys.exit(1)
except Exception as e:
    logging.error("Unexpected error: %s", e)
    sys.exit(1)
