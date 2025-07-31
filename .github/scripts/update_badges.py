import json
import re

# Read project metrics
with open('project_metrics.json', 'r') as f:
    data = json.load(f)

# Generate badge markdown
badges = []
for project in data['projects']:
    name = project['name'].replace(' ', '_')
    gain = project['gain']
    color = project['color']
    label_color = project['labelColor']
    badge_url = f"https://img.shields.io/badge/{name}-{gain}%25-{color}?labelColor={label_color}"
    badges.append(f"| {project['name']} | ![{project['name']} Gain]({badge_url}) |")

# Update README
with open('README.md', 'r') as f:
    content = f.read()

# Replace badge table content
new_table = "\n".join(badges)
pattern = r'(\| Project\s+\|\s+Performance Gain\s+\|\n\|[-]+\|\s*[-]+\|\n)([\s\S]*?)(?=\n\*)'
new_content = re.sub(pattern, f"\g<1>{new_table}", content)

with open('README.md', 'w') as f:
    f.write(new_content)