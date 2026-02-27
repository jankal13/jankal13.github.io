import json
import html
import yaml
from urllib.parse import urlparse

DEFAULT_TEXT_VAR = "Quarto Resume"

def clean_domain(url):
    if not url:
        return None
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    # Remove 'www.' if present
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def extract_name(title):
    """Extract the person's name from the title string (before the first '|')."""
    if title and '|' in title:
        return title.split("|")[0].strip()
    return title.strip() if title else "Resume"

def build_jsonld(title, description, custom_domain):
    """Build JSON-LD structured data for ATS and search engine crawlers."""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "ProfilePage",
        "mainEntity": {
            "@type": "Person",
            "name": extract_name(title),
            "description": description,
        }
    }
    if custom_domain:
        jsonld["mainEntity"]["url"] = f"https://{custom_domain}"
    return json.dumps(jsonld)

def pre_render():
    # Convert RESUME.json to _variables.yml
    with open('RESUME.json', 'r', encoding='utf-8') as json_file:
        meta_data = json.load(json_file)
    
    with open('_quarto-development.yml', 'w', encoding='utf-8') as yaml_file:
        google_analytics = meta_data.get("google-analytics", None)
        title = meta_data.get("title", "Resume")
        custom_domain = clean_domain(meta_data.get('custom-domain', None))
        secondary_email = meta_data.get('secondary-email', None)
        description = meta_data.get('description', DEFAULT_TEXT_VAR)
        keywords = ', '.join([secondary_email, custom_domain, DEFAULT_TEXT_VAR])
        author = extract_name(title)
        escaped_keywords = html.escape(keywords, quote=True)
        escaped_author = html.escape(author, quote=True)
        escaped_description = html.escape(description, quote=True)
        jsonld_script = f'<script type="application/ld+json">{build_jsonld(title, description, custom_domain)}</script>'
        header_meta = '\n'.join([
            f'<meta name="keywords" content="{escaped_keywords}">',
            f'<meta name="author" content="{escaped_author}">',
            '<meta name="robots" content="index, follow">',
            f'<meta name="description" content="{escaped_description}">',
            jsonld_script,
        ])
        development_profile = {
            "website": {
                "site-url": custom_domain,
                "page-footer": {
                    "center": [
                        {
                            "text": "Email me",
                            "href": f"mailto:{secondary_email}"
                        },
                        {
                            "text": "LinkedIn",
                            "href": "https://in.kalbantner.com"
                        },
                    ]
                },
            },
            "format": {
                "html": {
                    "description": description,
                    "output-file": "index.html",
                    "header-includes": header_meta,
                    "pagetitle": title,
                },
                "pdf": {
                    "output-file": "jan_kalbantner_resume.pdf"
                }
            }
        }
        if google_analytics:
            development_profile["website"]["google-analytics"] = google_analytics
        yaml.dump(development_profile, yaml_file, default_flow_style=False, encoding='utf-8')
    print("Created _quarto-development.yml from RESUME.json")

    # Check for custom-domain and create CNAME file if it exists
    if custom_domain:
        with open('CNAME', 'w') as cname_file:
            cname_file.write(custom_domain)
        print(f"Created CNAME file with domain: {custom_domain}")

if __name__ == "__main__":
    pre_render()
