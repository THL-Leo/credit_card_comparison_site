"""
Utility module for mapping credit card issuers to their Simple Icons.
Provides fallback to custom bank icon when specific issuer icon is not available.
"""

# Simple Icons CDN base URL
SIMPLE_ICONS_CDN = "https://cdn.jsdelivr.net/npm/simple-icons@v10/icons"

# Custom bank icon as data URL (your provided SVG)
CUSTOM_BANK_ICON_SVG = """<svg viewBox="0 0 1024 1024" class="icon" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M511.8 154.1L916 277v45.7H108V277l403.8-122.9m0-46L64 244.4v122.3h896V244.4L511.8 108.1zM113 831.4h798v16H113z" fill="#39393A"></path><path d="M113 391.1h798v16H113z" fill="#E73B37"></path><path d="M64.3 871.8h895.3v44H64.3zM204.2 475.6v287.3h52v44h-120v-44h52V475.6h-52v-44h120v44zM414.7 475.6v287.3h52v44h-120v-44h52V475.6h-52v-44h120v44zM625.2 475.6v287.3h52v44h-120v-44h52V475.6h-52v-44h120v44zM835.8 475.6v287.3h52v44h-120v-44h52V475.6h-52v-44h120v44z" fill="#39393A"></path></g></svg>"""

# Convert custom SVG to data URL
import base64
GENERIC_BANK_ICON = f"data:image/svg+xml;base64,{base64.b64encode(CUSTOM_BANK_ICON_SVG.encode()).decode()}"

# Mapping of issuer names to their Simple Icons slug
ISSUER_ICON_MAP = {
    # Major Banks
    "Chase": "chase",
    "JPMorgan Chase": "chase",
    "American Express": "americanexpress",
    "Amex": "americanexpress",
    "Capital One": "capitalone",
    "Citi": "citi",  # Fixed: Use citigroup instead of citi
    "Citibank": "citi",
    "Bank of America": "bankofamerica",
    "Wells Fargo": "wellsfargo",
    "Discover": "discover",
    "US Bank": "usbank",
    "U.S. Bank": "usbank",
    
    # International Banks
    "Barclays": "barclays",
    "HSBC": "hsbc",
    "TD Bank": "td",
    "RBC": "rbc",
    "BMO": "bmo",
    "Scotiabank": "scotiabank",
    
    # Credit Unions
    "Navy Federal Credit Union": "navyfederal",
    "USAA": "usaa",
    "PenFed Credit Union": "pentagon",  # Pentagon Federal
    
    # Tech/Digital Banks
    "Goldman Sachs": "goldmansachs",
    "Marcus": "goldmansachs",  # Marcus by Goldman Sachs
    "Apple": "apple",  # For Apple Card
    "PayPal": "paypal",
    "Venmo": "venmo",
    
    # Other Financial Institutions
    "Synchrony": "synchrony",
    "Ally": "ally",
    "SoFi": "sofi",
    "Chime": "chime",
    "Robinhood": "robinhood",
}

def get_default_icon_url() -> str:
    return GENERIC_BANK_ICON

def get_issuer_icon_url(issuer_name: str) -> str:
    """
    Get the Simple Icons URL for a given issuer name.
    
    Args:
        issuer_name (str): The name of the credit card issuer
        
    Returns:
        str: URL to the issuer's icon or custom bank icon if not found
    """
    if not issuer_name:
        return GENERIC_BANK_ICON
    
    # Clean up the issuer name for better matching
    cleaned_name = issuer_name.strip()
    
    # Try exact match first
    if cleaned_name in ISSUER_ICON_MAP:
        icon_slug = ISSUER_ICON_MAP[cleaned_name]
        return f"{SIMPLE_ICONS_CDN}/{icon_slug}.svg"
    
    # Try case-insensitive match
    for issuer, icon_slug in ISSUER_ICON_MAP.items():
        if issuer.lower() == cleaned_name.lower():
            return f"{SIMPLE_ICONS_CDN}/{icon_slug}.svg"
    
    # Try partial match (for cases like "Chase Bank" -> "Chase")
    for issuer, icon_slug in ISSUER_ICON_MAP.items():
        if issuer.lower() in cleaned_name.lower() or cleaned_name.lower() in issuer.lower():
            return f"{SIMPLE_ICONS_CDN}/{icon_slug}.svg"
    
    # Return custom bank icon if no match found
    return GENERIC_BANK_ICON

def get_issuer_icon_data_url(issuer_name: str, color: str = "#000000") -> str:
    """
    Get a data URL for the issuer icon with custom color.
    This is useful for inline SVG with custom styling.
    
    Args:
        issuer_name (str): The name of the credit card issuer
        color (str): Hex color code for the icon (default: black)
        
    Returns:
        str: Data URL for the SVG icon
    """
    # For now, return the regular URL
    # In the future, this could fetch and modify SVG colors
    return get_issuer_icon_url(issuer_name)

def get_custom_bank_icon_with_color(color: str = "#39393A") -> str:
    """
    Get the custom bank icon with a specific color.
    
    Args:
        color (str): Hex color code for the icon
        
    Returns:
        str: Data URL for the colored SVG icon
    """
    colored_svg = CUSTOM_BANK_ICON_SVG.replace('fill="#39393A"', f'fill="{color}"')
    return f"data:image/svg+xml;base64,{base64.b64encode(colored_svg.encode()).decode()}"

def update_issuer_icons_in_database():
    """
    SQL script to update all issuer logo_url fields with Simple Icons URLs.
    This function returns the SQL commands to run.
    
    Returns:
        str: SQL UPDATE statements
    """
    sql_updates = []
    
    for issuer_name, icon_slug in ISSUER_ICON_MAP.items():
        icon_url = f"{SIMPLE_ICONS_CDN}/{icon_slug}.svg"
        sql_updates.append(
            f"UPDATE issuers SET logo_url = '{icon_url}' WHERE name = '{issuer_name}';"
        )
    
    # Update any remaining issuers with custom bank icon
    # Note: We'll use a placeholder URL that the application will replace with the data URL
    generic_update = f"""
UPDATE issuers 
SET logo_url = 'CUSTOM_BANK_ICON' 
WHERE logo_url = '/placeholder.svg' OR logo_url IS NULL OR logo_url = '';
"""
    sql_updates.append(generic_update)
    
    return "\n".join(sql_updates)

# Color schemes for different issuers (optional)
ISSUER_COLORS = {
    "Chase": "#117ACA",
    "American Express": "#006FCF",
    "Capital One": "#004879",
    "Citi": "#056DAE",
    "Bank of America": "#E31837",
    "Wells Fargo": "#D71921",
    "Discover": "#FF6000",
    "US Bank": "#0F4C81",
    "Barclays": "#00AEEF",
    "Goldman Sachs": "#0066CC",
    "Apple": "#000000",
    "USAA": "#003366",
}

def get_issuer_color(issuer_name: str) -> str:
    """
    Get the brand color for an issuer.
    
    Args:
        issuer_name (str): The name of the credit card issuer
        
    Returns:
        str: Hex color code for the issuer's brand color
    """
    return ISSUER_COLORS.get(issuer_name, "#4A5568")  # Default gray color 