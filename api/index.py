"""
Krafti Backend API (Vercel Serverless Function)
FastAPI server for image processing, description generation, and price estimation
"""
import os
import io
import base64
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import google.generativeai as genai


# Import from SAME directory (api.price_estimator)
# When running in Vercel, this file is the entry point
try:
    from api.price_estimator import calculate_price_range, parse_keywords_from_description
except ImportError:
    # Local fallback or standard import
    from price_estimator import calculate_price_range, parse_keywords_from_description


# Load environment variables
load_dotenv()

# Configure Groq API
from groq import Groq
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))



app = FastAPI(title="Krafti API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def remove_background_api(image_bytes: bytes) -> bytes:
    """Remove background using remove.bg API."""
    response = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        files={"image_file": image_bytes},
        data={"size": "auto"},
        headers={"X-Api-Key": REMOVEBG_API_KEY},
    )
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"remove.bg API error: {response.status_code} - {response.text}")


@app.get("/")
async def root():
    return {"message": "Krafti API is running", "version": "1.0.0"}

@app.get("/api/python")
async def root_api():
    return {"message": "Krafti API (Python Runtime) is running"}

@app.post("/process-image") # Alias for Vercel path stripping
@app.post("/api/process-image")
async def process_image(file: UploadFile = File(...)):
    """
    Process uploaded craft image:
    1. Analyze image using Gemini (Description + Prompt)
    2. Generate Background using Pixelcut (Auto-remove BG + Generate)
    3. Calculate price range
    """
    try:
        # Read image
        contents = await file.read()
        original_image = Image.open(io.BytesIO(contents)).convert("RGBA")
        
        # Optimization: We SKIP explicit RemoveBG step to save time (Vercel 10s timeout).
        # Pixelcut API automatically removes background if we send the product image.
        
        # Step 1: Generate description and attributes using Groq (Llama Vision)
        print("Starting Groq Vision analysis...")
        
        # Prepare image for Groq (needs base64 data URI)
        # Resize if too large to save tokens/latency
        max_size = (1024, 1024)
        groq_image = original_image.copy()
        groq_image.thumbnail(max_size)
        img_b64_str = image_to_base64(groq_image, "JPEG")
        data_url = f"data:image/jpeg;base64,{img_b64_str}"

        # Using structured prompt for better results
        analysis_prompt = (
            "Analyze this handmade craft product image and generate a JSON response containing:\n"
            "1. 'description': A persuasive, high-quality e-commerce product description (2-3 sentences) that highlights craftsmanship, materials, and emotional appeal. Use selling language.\n"
            "2. 'background_prompt': A short, specific prompt for a professional background (e.g. 'marble table', 'wooden desk').\n"
            "3. 'attributes': A dictionary with the following keys:\n"
            "   - 'category': One of ['jewelry', 'home_decor', 'clothing', 'art', 'pottery', 'other']\n"
            "   - 'material': One of ['fabric', 'wood', 'metal', 'ceramic', 'paper', 'mixed', 'unknown']\n"
            "   - 'size': One of ['small', 'medium', 'large'] (Estimate based on standard object sizes)\n"
            "   - 'quality': One of ['basic', 'handmade', 'premium', 'artisan'] (Assess visual intricacy)\n"
            "\n"
            "Output MUST be valid JSON only. No markdown formatting. Do not output explanations."
        )

        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_url,
                                },
                            },
                        ],
                    }
                ],
                model="llama-3.2-11b-vision-preview",
                temperature=0.5,
                max_tokens=1024,
                top_p=1,
                stream=False,
                response_format={"type": "json_object"},
            )
            
            analysis_text = chat_completion.choices[0].message.content
            print("Received JSON analysis from Groq.")
            
            import json
            data = json.loads(analysis_text.strip())
            
            description = data.get("description", "Handmade craft product.")
            bg_prompt_text = data.get("background_prompt", "minimalist professional studio background")
            attributes = data.get("attributes", {})
            
        except Exception as e_groq:
            print(f"Groq Analysis Failed: {e_groq}")
            description = "Handmade craft product (Analysis failed)."
            bg_prompt_text = "minimalist professional studio background"
            attributes = {}

        # Step 2: Generate Background Image using Pixelcut API
        # We pass the ORIGINAL image. Pixelcut removes background and composites.
        # Strategy: Direct Remove.bg API (Simplest, Most Robust)
        # No complex hosting, no heavy libraries, just a clean API call.
        print("Using Remove.bg API...")
        
        try:
            # 1. Remove Background
            img_byte_arr = io.BytesIO()
            original_image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # Using the helper function defined above which uses the API key from env
            no_bg_bytes = remove_background_api(img_bytes)
            
            no_bg_image = Image.open(io.BytesIO(no_bg_bytes)).convert("RGBA")
            
            # 2. Add Professional White Background
            # This is standard for e-commerce and always looks good
            white_bg = Image.new("RGBA", no_bg_image.size, "WHITE")
            final_image = Image.alpha_composite(white_bg, no_bg_image).convert("RGB")
            
            description += " (Enhanced with professional studio background)"
            
        except Exception as e_process:
            print(f"Background removal failed: {e_process}")
            # Fallback to original image if even Remove.bg fails
            final_image = original_image.convert("RGB")

        # Convert processed image to base64
        processed_image_b64 = image_to_base64(final_image, "JPEG")
        
        # Step 3: Calculate price using AI-extracted attributes
        # Map Gemini attributes to PriceFactors keys if needed, but they should match
        price_factors = {
            "size": attributes.get("size", "medium").lower(),
            "material": attributes.get("material", "mixed").lower(),
            "quality": attributes.get("quality", "handmade").lower(),
            "category": attributes.get("category", "other").lower()
        }
        
        # Ensure regex fallback if attributes are missing/empty (e.g. Gemini failure)
        if not price_factors["category"] or price_factors["category"] == "unknown":
             from api.price_estimator import parse_keywords_from_description
             # Fallback to regex parsing if AI didn't give good tags
             price_factors = parse_keywords_from_description(description)
             
        min_price, max_price, confidence = calculate_price_range(price_factors)
        
        return JSONResponse({
            "success": True,
            "processed_image": f"data:image/jpeg;base64,{processed_image_b64}",
            "description": description,
            "price_range": {
                "min": min_price,
                "max": max_price,
                "currency": "INR"
            },
            "confidence": round(confidence, 1),
            "detected_attributes": {
                "size": price_factors["size"],
                "material": price_factors["material"],
                "quality": price_factors["quality"],
                "category": price_factors["category"]
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
