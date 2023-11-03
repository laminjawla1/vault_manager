def gmd(value):
    """Format value as GMD"""
    if not "GMD" in str(value):
        return f"GMD {value:,.2f}"
    return value