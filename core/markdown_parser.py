import re

def parse_changelog(text: str, mode: str, application_version: str) -> str:
    """Parses a raw markdown text into HTML"""
    html_output: str = "<style>h2 {color: #2c3e50;} h3 {color: #2980b9;} ul {line-height: 1.6;}</style>"
    
    sections: list[str] = re.split(r'(?:^|\n)## ', text)
    sections = [section for section in sections if section.strip()]
    
    if not sections:
        return "<p>No changelog data found.</p>"
    
    valid_versions: list[str] = []
    for section in sections:
        if section.startswith("#"):
            continue
        valid_versions.append(section)
    
    if not valid_versions:
        return "<p>No version information found.</p>"
    
    latest_section: str = valid_versions[0]
    past_sections: list[str] = valid_versions[1:]
    
    if mode == "fixes":
        html_output += f"<h2>Latest Changes & Fixes - v{application_version}</h2>"
        
        sub_sections: list[str] = re.split(r'(?:^|\n)### ', latest_section)
        found_relevant: bool = False
        
        for sub in sub_sections:
            header_match = re.match(r'([A-Za-z ]+)', sub)
            if header_match:
                header: str = header_match.group(1).strip()
                if header in ["Fixed", "Changed"]:
                    found_relevant = True
                    body: str = sub[len(header):].strip()
                    html_output += f"<h3>{header}</h3>"
                    html_output += _markdown_list_to_html(body)
        if not found_relevant:
            html_output += "<p>No bug fixes or changes listed for the latest version.</p>"
    
    elif mode == "history":
        html_output += "<h2>Version History</h2>"
        if not past_sections:
            html_output += "<p>No past versions found.</p>"
            
        for version_text in past_sections:
            lines: list[str] = version_text.split('\n')
            version_title: str = lines[0].strip()
            html_output += f"<hr><h3>{version_title}</h3>"
            
            body: str = "\n".join(lines[1:])
            body = re.sub(r'### (.*?)\n', r'<h4>\1</h4>\n', body)
            html_output += _markdown_list_to_html(body)

    return html_output

def _markdown_list_to_html(text: str) -> str:
    """Helper function to convert markdown bullet list to HTML li element"""
    lines: list[str] = text.split("\n")
    html: str = ""
    in_list: bool = False
    
    for line in lines:
        stripped: str = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html += "<ul>"
                in_list = True
                
            content: str = stripped[2:]
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
            html += f"<li>{content}</li>"
            
        elif not stripped:
            if in_list:
                html += "</ul>"
                in_list = False
                
        else:
            if in_list:
                html += "</ul>"
                in_list = False
            html += f"<p>{stripped}</p>"
    
    if in_list:
        html += "</ul>"
        
    return html