"""
Price Estimator Module for Krafti
Uses Python typing to match keywords with price ranges
"""
from typing import TypedDict, Literal, Tuple

class PriceFactors(TypedDict):
    size: Literal["small", "medium", "large", "unknown"]
    material: Literal["fabric", "wood", "metal", "ceramic", "paper", "mixed", "unknown"]
    quality: Literal["basic", "handmade", "premium", "artisan", "unknown"]
    category: Literal["jewelry", "home_decor", "clothing", "art", "pottery", "other"]

# Base prices in INR
CATEGORY_BASE = {
    "jewelry": 500,
    "home_decor": 800,
    "clothing": 600,
    "art": 1000,
    "pottery": 700,
    "other": 500
}

SIZE_MULTIPLIER = {
    "small": 0.7,
    "medium": 1.0,
    "large": 1.5,
    "unknown": 1.0
}

MATERIAL_MULTIPLIER = {
    "fabric": 0.8,
    "wood": 1.2,
    "metal": 1.5,
    "ceramic": 1.3,
    "paper": 0.5,
    "mixed": 1.0,
    "unknown": 1.0
}

QUALITY_MULTIPLIER = {
    "basic": 0.8,
    "handmade": 1.3,
    "premium": 1.8,
    "artisan": 2.5,
    "unknown": 1.0
}


def calculate_price_range(factors: PriceFactors) -> Tuple[int, int, float]:
    """
    Calculate price range based on extracted keywords.
    
    Returns:
        Tuple of (min_price, max_price, confidence)
    """
    base = CATEGORY_BASE.get(factors["category"], 500)
    
    size_mult = SIZE_MULTIPLIER.get(factors["size"], 1.0)
    material_mult = MATERIAL_MULTIPLIER.get(factors["material"], 1.0)
    quality_mult = QUALITY_MULTIPLIER.get(factors["quality"], 1.0)
    
    # Calculate base price
    calculated_price = base * size_mult * material_mult * quality_mult
    
    # Create a range (±20%)
    min_price = int(calculated_price * 0.8)
    max_price = int(calculated_price * 1.2)
    
    # Calculate confidence based on known factors
    known_factors = sum([
        1 if factors["size"] != "unknown" else 0,
        1 if factors["material"] != "unknown" else 0,
        1 if factors["quality"] != "unknown" else 0,
        1 if factors["category"] != "other" else 0
    ])
    
    confidence = (known_factors / 4) * 100  # Percentage
    
    return min_price, max_price, confidence


def parse_keywords_from_description(description: str) -> PriceFactors:
    """
    Extract price factors from AI-generated description.
    """
    description_lower = description.lower()
    
    # Detect size
    size: Literal["small", "medium", "large", "unknown"] = "unknown"
    if any(word in description_lower for word in ["small", "mini", "tiny", "compact"]):
        size = "small"
    elif any(word in description_lower for word in ["large", "big", "oversized", "xl"]):
        size = "large"
    elif any(word in description_lower for word in ["medium", "regular", "standard"]):
        size = "medium"
    
    # Detect material
    material: Literal["fabric", "wood", "metal", "ceramic", "paper", "mixed", "unknown"] = "unknown"
    if any(word in description_lower for word in ["fabric", "cotton", "silk", "cloth", "textile", "woven"]):
        material = "fabric"
    elif any(word in description_lower for word in ["wood", "wooden", "bamboo", "timber"]):
        material = "wood"
    elif any(word in description_lower for word in ["metal", "brass", "copper", "iron", "steel", "silver", "gold"]):
        material = "metal"
    elif any(word in description_lower for word in ["ceramic", "clay", "pottery", "terracotta"]):
        material = "ceramic"
    elif any(word in description_lower for word in ["paper", "cardboard", "papier"]):
        material = "paper"
    
    # Detect quality
    quality: Literal["basic", "handmade", "premium", "artisan", "unknown"] = "unknown"
    if any(word in description_lower for word in ["artisan", "artisanal", "master", "exquisite", "luxury"]):
        quality = "artisan"
    elif any(word in description_lower for word in ["premium", "high-quality", "finest", "superior"]):
        quality = "premium"
    elif any(word in description_lower for word in ["handmade", "handcrafted", "hand-made", "hand crafted"]):
        quality = "handmade"
    elif any(word in description_lower for word in ["basic", "simple", "plain"]):
        quality = "basic"
    
    # Detect category
    category: Literal["jewelry", "home_decor", "clothing", "art", "pottery", "other"] = "other"
    if any(word in description_lower for word in ["necklace", "bracelet", "earring", "ring", "jewelry", "jewellery", "pendant"]):
        category = "jewelry"
    elif any(word in description_lower for word in ["vase", "lamp", "decor", "decoration", "frame", "mirror", "candle"]):
        category = "home_decor"
    elif any(word in description_lower for word in ["dress", "shirt", "scarf", "bag", "purse", "clothing", "wear"]):
        category = "clothing"
    elif any(word in description_lower for word in ["painting", "art", "canvas", "sculpture", "statue"]):
        category = "art"
    elif any(word in description_lower for word in ["pot", "bowl", "plate", "pottery", "ceramic"]):
        category = "pottery"
    
    return PriceFactors(
        size=size,
        material=material,
        quality=quality,
        category=category
    )
