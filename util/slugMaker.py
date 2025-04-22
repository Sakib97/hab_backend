import re

def slugify(string):
    """
    Convert a string into a URL-friendly slug.
    """
    # Convert to lowercase
    string = string.lower()
    
    # Replace all non-alphanumeric characters (except spaces) with a hyphen
    cleaned_string = re.sub(r'[^\w\s]', '-', string)

    # Replace any remaining spaces with hyphens
    cleaned_string = re.sub(r'\s+', '-', cleaned_string)

    # Remove any consecutive hyphens and leading/trailing hyphens
    cleaned_string = re.sub(r'-+', '-', cleaned_string).strip('-')
    
    return cleaned_string