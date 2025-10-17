import json
import csv
import os
from pathlib import Path
from collections import defaultdict

# CWE Top 25 for 2024
CWE_TOP_25 = [
    'CWE-79', 'CWE-787', 'CWE-89', 'CWE-416', 'CWE-78', 'CWE-20', 'CWE-125',
    'CWE-22', 'CWE-352', 'CWE-434', 'CWE-862', 'CWE-476', 'CWE-287', 'CWE-190',
    'CWE-502', 'CWE-77', 'CWE-119', 'CWE-798', 'CWE-918', 'CWE-306', 'CWE-362',
    'CWE-269', 'CWE-94', 'CWE-863', 'CWE-276'
]

def extract_cwe_from_bandit(data):
    """Extract CWE findings from Bandit JSON output"""
    cwe_map = defaultdict(int)
    
    if 'results' in data:
        for finding in data['results']:
            cwe_id = None
            
            # Try to get CWE from various fields
            if 'issue_cwe' in finding:
                if isinstance(finding['issue_cwe'], dict) and 'id' in finding['issue_cwe']:
                    cwe_id = str(finding['issue_cwe']['id'])
                elif isinstance(finding['issue_cwe'], (str, int)):
                    cwe_id = str(finding['issue_cwe'])
            
            # Try extracting from issue_text
            if not cwe_id and 'issue_text' in finding:
                import re
                match = re.search(r'CWE-\d+', finding['issue_text'])
                if match:
                    cwe_id = match.group(0)
            
            # Normalize CWE ID format
            if cwe_id:
                cwe_id = str(cwe_id)  # Ensure it's a string
                if not cwe_id.startswith('CWE-'):
                    cwe_id = f'CWE-{cwe_id}'
                cwe_map[cwe_id] += 1
    
    return cwe_map

def extract_cwe_from_semgrep(data):
    """Extract CWE findings from Semgrep JSON output"""
    cwe_map = defaultdict(int)
    
    if 'results' in data:
        for finding in data['results']:
            cwe_id = None
            
            # Check in metadata
            if 'extra' in finding and 'metadata' in finding['extra']:
                metadata = finding['extra']['metadata']
                if 'cwe' in metadata:
                    cwe = metadata['cwe']
                    # CWE can be a list or single value
                    if isinstance(cwe, list):
                        for c in cwe:
                            cwe_id = f'CWE-{c}' if not str(c).startswith('CWE-') else str(c)
                            cwe_map[cwe_id] += 1
                        continue
                    else:
                        cwe_id = f'CWE-{cwe}' if not str(cwe).startswith('CWE-') else str(cwe)
            
            if cwe_id:
                cwe_map[cwe_id] += 1
    
    return cwe_map


def extract_cwe_from_safety(data):
    """Extract CWE findings from Safety JSON output"""
    import re
    cwe_map = defaultdict(int)
    
    # Common CVE to CWE mappings for dependency vulnerabilities (fallback)
    DEFAULT_DEPENDENCY_CWES = {
        'injection': 'CWE-94',
        'command injection': 'CWE-77',
        'deserialization': 'CWE-502',
        'xxe': 'CWE-611',
        'traversal': 'CWE-22',
        'path traversal': 'CWE-22',
        'sql': 'CWE-89',
        'xss': 'CWE-79',
        'cross-site scripting': 'CWE-79',
        'csrf': 'CWE-352',
        'denial of service': 'CWE-400',
        'dos': 'CWE-400',
        'buffer overflow': 'CWE-120',
        'authentication': 'CWE-287',
        'authorization': 'CWE-285',
        'cryptographic': 'CWE-327',
        'encryption': 'CWE-327',
        'information disclosure': 'CWE-200',
        'redirect': 'CWE-601',
        'ssrf': 'CWE-918',
        'regex': 'CWE-1333',
    }
    
    # Safety 3.x has vulnerabilities at top level
    vulnerabilities = []
    
    if 'vulnerabilities' in data and data['vulnerabilities']:
        vulnerabilities = data['vulnerabilities']
    elif 'scanned_packages' in data:
        # Fallback: check inside packages
        for package_name, package_info in data['scanned_packages'].items():
            if 'vulnerabilities' in package_info and package_info['vulnerabilities']:
                vulnerabilities.extend(package_info['vulnerabilities'])
    
    for vuln in vulnerabilities:
        cwe_id = None
        
        # Check advisory field for CWE (this is where Safety includes it!)
        if 'advisory' in vuln and vuln['advisory']:
            advisory = str(vuln['advisory'])
            # Look for patterns like "CWE-77:", "CWE-77 ", "tracked under CWE-77"
            match = re.search(r'CWE[-:\s]*(\d+)', advisory, re.IGNORECASE)
            if match:
                cwe_id = f'CWE-{match.group(1)}'
        
        # Try other direct fields
        if not cwe_id:
            for field in ['cwe', 'cwe_id', 'CWE']:
                if field in vuln and vuln[field]:
                    cwe_id = str(vuln[field])
                    break
        
        # Search in the entire vulnerability object
        if not cwe_id:
            vuln_str = json.dumps(vuln)
            match = re.search(r'CWE[-:\s]*(\d+)', vuln_str, re.IGNORECASE)
            if match:
                cwe_id = f'CWE-{match.group(1)}'
        
        # If no CWE found, try mapping based on advisory description
        if not cwe_id:
            vuln_text = ''
            if 'advisory' in vuln:
                vuln_text += str(vuln['advisory']).lower()
            if 'vulnerability_id' in vuln:
                vuln_text += str(vuln['vulnerability_id']).lower()
            
            # Try to match keywords
            for keyword, cwe in DEFAULT_DEPENDENCY_CWES.items():
                if keyword in vuln_text:
                    cwe_id = cwe
                    break
            
            # If still no match, use default for vulnerable dependency
            if not cwe_id:
                cwe_id = 'CWE-1035'  # Vulnerable Third-Party Component
        
        # Normalize CWE format
        if cwe_id:
            cwe_id = str(cwe_id).upper()
            if not cwe_id.startswith('CWE-'):
                cwe_id = f'CWE-{cwe_id}'
            cwe_map[cwe_id] += 1
    
    return cwe_map

def process_json_file(file_path, project_name, tool_name):
    """Process a single JSON file and extract CWE findings"""
    print(f"Processing {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
            # Check if file is empty or has invalid JSON
            if not content:
                print(f"Warning: {file_path} is empty.")
                return []
            
            # Safety files may have deprecation warnings before/after JSON
            # Try to extract just the JSON part
            if tool_name.lower() == 'safety':
                # Find the start and end of JSON
                json_start = content.find('{')
                if json_start == -1:
                    print(f"Warning: Could not find JSON in {file_path}")
                    return []
                
                # Find matching closing brace by counting braces
                brace_count = 0
                json_end = json_start
                for i in range(json_start, len(content)):
                    if content[i] == '{':
                        brace_count += 1
                    elif content[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = i + 1
                            break
                
                content = content[json_start:json_end]
            
            # Try to parse JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Warning: {file_path} contains invalid JSON: {e}")
                print(f"First 100 chars: {content[:100]}")
                return []
        
        # Extract CWE based on tool
        tool_lower = tool_name.lower()
        if tool_lower == 'bandit':
            cwe_map = extract_cwe_from_bandit(data)
        elif tool_lower == 'semgrep':
            cwe_map = extract_cwe_from_semgrep(data)
        elif tool_lower == 'safety':
            cwe_map = extract_cwe_from_safety(data)
        else:
            print(f"Warning: Unknown tool '{tool_name}'. Using generic extraction.")
            # Generic extraction - search for CWE patterns in entire JSON
            import re
            json_str = json.dumps(data)
            matches = re.findall(r'CWE-\d+', json_str)
            cwe_map = defaultdict(int)
            for cwe in matches:
                cwe_map[cwe] += 1
        
        # Convert to list of dictionaries
        results = []
        for cwe_id, count in cwe_map.items():
            results.append({
                'project': project_name,
                'tool': tool_name,
                'cwe_id': cwe_id,
                'count': count,
                'is_top_25': 'Yes' if cwe_id in CWE_TOP_25 else 'No'
            })
        
        if results:
            print(f"  ✓ Found {len(results)} unique CWEs, {sum(r['count'] for r in results)} total findings")
        else:
            print(f"  ⚠ No CWE findings extracted")
        
        return results
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    # Configuration
    INPUT_DIR = 'results'  # Directory containing JSON files
    OUTPUT_CSV = 'consolidated_cwe_findings.csv'
    
    # File naming convention: projectname_toolname.json
    # e.g., django_bandit.json, ansible_semgrep.json
    
    all_results = []
    
    # Check if input directory exists
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Directory '{INPUT_DIR}' not found.")
        print("Please create a 'results' directory and place your JSON files there.")
        print("\nExpected file naming: projectname_toolname.json")
        print("Examples:")
        print("  - django_bandit.json")
        print("  - ansible_semgrep.json")
        print("  - airflow_safety.json")
        return
    
    # Process all JSON files in the directory
    json_files = list(Path(INPUT_DIR).glob('*.json'))
    
    if not json_files:
        print(f"No JSON files found in '{INPUT_DIR}' directory.")
        return
    
    print(f"Found {len(json_files)} JSON files to process.\n")
    
    for file_path in json_files:
        filename = file_path.stem  # Get filename without extension
        
        # Parse filename to extract project and tool
        parts = filename.split('_')
        
        if len(parts) < 2:
            print(f"Warning: Skipping '{file_path.name}' - invalid filename format.")
            print("Expected format: projectname_toolname.json")
            continue
        
        project_name = parts[0]
        tool_name = parts[1]
        
        # Process the file
        results = process_json_file(file_path, project_name, tool_name)
        all_results.extend(results)
    
    # Write to CSV
    if all_results:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Project_name', 'Tool_name', 'CWE_ID', 'Number_of_Findings', 'Is_In_CWE_Top_25']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in all_results:
                writer.writerow({
                    'Project_name': result['project'],
                    'Tool_name': result['tool'],
                    'CWE_ID': result['cwe_id'],
                    'Number_of_Findings': result['count'],
                    'Is_In_CWE_Top_25': result['is_top_25']
                })
        
        print(f"\n✓ Successfully created '{OUTPUT_CSV}'")
        print(f"  Total entries: {len(all_results)}")
        print(f"  Unique CWEs: {len(set(r['cwe_id'] for r in all_results))}")
        print(f"  Total findings: {sum(r['count'] for r in all_results)}")
        
        # Summary by project and tool
        print("\n--- Summary ---")
        projects = set(r['project'] for r in all_results)
        tools = set(r['tool'] for r in all_results)
        print(f"Projects: {', '.join(sorted(projects))}")
        print(f"Tools: {', '.join(sorted(tools))}")
        
    else:
        print("\nNo CWE findings extracted from any files.")

if __name__ == "__main__":
    main()