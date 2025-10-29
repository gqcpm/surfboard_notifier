"""
Prompts for Gemini AI classification.
"""

# Main classification prompt template
CLASSIFICATION_PROMPT_TEMPLATE = """
Analyze these surfboard listings and classify each one as MIDLENGTH, LONGBOARD, SHORTBOARD, or OTHER.

{listings_text}

Classification criteria:
- LONGBOARD: 8 feet and longer, typically 9-10+ feet, designed for cruising and noseriding. Includes noserider, log, and traditional longboards. Must be 8ft+ OR explicitly described as noserider/longboard
- MIDLENGTH: 7-8 feet, hybrid between shortboard and longboard, good for intermediate surfers  
- SHORTBOARD: Under 7 feet, high-performance boards for advanced surfers. Includes 5'7", 5'8", 5'9", 5'10", 5'11", 6'0", 6'1", 6'2" boards
- OTHER: Wetsuits, accessories, non-surfboard items, routers, modems, clothing, or unclear descriptions

IMPORTANT: 
- 6ft and under boards are SHORTBOARD, NOT longboard
- 5'7", 5'8", 5'9", 5'10", 5'11" are all SHORTBOARD
- Routers, modems, wetsuits, clothing = OTHER
- Noserider boards = LONGBOARD (they are longboards)
- Only keep LONGBOARD (8ft+ or noserider)
- Be strict about length requirements

Respond with ONLY the classification for each listing in order, separated by newlines:
1. [CLASSIFICATION]
2. [CLASSIFICATION]
etc.
"""

# Listing text format template
LISTING_FORMAT_TEMPLATE = """
{i}. Title: {title}
   Description: {description}
   Price: {price}
"""
