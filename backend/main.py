"""
Krafti Backend API
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
from PIL import Image, ImageFilter
import google.generativeai as genai

from price_estimator import calculate_price_range, parse_keywords_from_description
from PIL import Image



# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Remove.bg API
REMOVEBG_API_KEY = os.getenv("REMOVEBG_API_KEY")

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


@app.post("/api/process-image")
async def process_image(file: UploadFile = File(...)):
    """
    Process uploaded craft image:
    1. Remove background using remove.bg API
    2. Generate product description using Gemini
    3. Calculate price range based on keywords
    """
    try:
        # Read image
        contents = await file.read()
        original_image = Image.open(io.BytesIO(contents)).convert("RGBA")
        
        # Step 1: Remove background using remove.bg API
        try:
            no_bg_bytes = remove_background_api(contents)
            image_no_bg = Image.open(io.BytesIO(no_bg_bytes)).convert("RGBA")
        except Exception as e:
            # If remove.bg fails, use original image with message
            print(f"Background removal failed: {e}")
            image_no_bg = original_image
        

        
        # Convert processed image to base64

        
        # Step 3: Generate description and background prompt using Gemini
        print("Starting Gemini analysis...")
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Convert image for Gemini (it accepts PIL Image directly)
        description_image = original_image.convert("RGB")
        
        analysis_prompt = """Analyze this handmade craft product image and generate:
1. A brief e-commerce description (2-3 sentences).
2. A short, specific prompt to generate a matching professional background for this product (e.g. "marble table", "wooden desk", "soft fabric").

Format:
Description: [Description]
Background Prompt: [Prompt]"""

        response = model.generate_content([analysis_prompt, description_image])
        analysis_text = response.text.strip()
        print("Received analysis from Gemini.")
        
        # Parse description and background prompt
        description = "Handmade craft product."
        bg_prompt_text = "minimalist professional studio background, soft lighting, 4k"
        
        try:
            lines = analysis_text.split('\n')
            desc_lines = []
            capture_desc = False
            for line in lines:
                if line.startswith("Description:"):
                    capture_desc = True
                    desc_lines.append(line.replace("Description:", "").strip())
                elif line.startswith("Background Prompt:"):
                    capture_desc = False
                    bg_prompt_text = line.replace("Background Prompt:", "").strip()
                elif capture_desc:
                    desc_lines.append(line)
            
            if desc_lines:
                description = " ".join(desc_lines).strip()
        except:
            print("Failed to parse specific sections, using raw text.")
            description = analysis_text

        # Step 4: Generate Background Image using Pollinations (PixelArt/Generative alternative)


# Remove global add_drop_shadow
# Revert compositing logic
        # Step 4: Generate Background Image using Pixelcut API
        print(f"Generating background via Pixelcut for prompt: {bg_prompt_text}")
        try:
            pixelcut_key = os.getenv("PIXELCUT_API_KEY")
            if not pixelcut_key:
                print("Warning: PIXELCUT_API_KEY not found in environment variables.")

            # Optimize prompt for Pixelcut - Glassy Reflection
            bg_gen_prompt = f"professional product photography background, on a glassy reflective surface, reflection of the object, glossy, {bg_prompt_text}, soft natural lighting, realistic shadows, high quality, 8k, photorealistic"
            
            print(f"Requesting Pixelcut with prompt: {bg_gen_prompt}")
            
            # Prepare image for download/upload
            # Pixelcut doc says "image_url", but often API supports multipart 'image' or 'file'.
            # We will try standard multipart first for local file.
            
            # Save current no-bg image to buffer
            img_byte_arr = io.BytesIO()
            image_no_bg.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Pixelcut 'generate-background' endpoint
            url = "https://api.developer.pixelcut.ai/v1/generate-background"
            
            payload = {
                "prompt": bg_gen_prompt,
                "format": "jpeg" # Optional, usually return URL or binary
            }
            files = {
                "image": ("image.png", img_byte_arr, "image/png")
            }
            headers = {
                "X-API-KEY": pixelcut_key or "",
                # Content-Type is auto-set by requests for multipart
            }
            
            # Note: If Pixelcut strictly requires URL, this might fail with 400.
            # But most modern AI APIs support direct uploads.
            
            resp = requests.post(url, headers=headers, data=payload, files=files)
            
            if resp.status_code == 200:
                # Pixelcut normally returns a JSON with "result_url" or directly the image?
                # Documentation usually says "result_url".
                # Let's check response content type.
                content_type = resp.headers.get("Content-Type", "")
                
                if "application/json" in content_type:
                    data = resp.json()
                    # Check for url
                    if "result_url" in data:
                        img_url = data["result_url"]
                        img_resp = requests.get(img_url)
                        background_image = Image.open(io.BytesIO(img_resp.content)).convert("RGBA")
                    elif "image_url" in data: # variation
                        img_url = data["image_url"]
                        img_resp = requests.get(img_url)
                        background_image = Image.open(io.BytesIO(img_resp.content)).convert("RGBA")
                    else:
                        print(f"Pixelcut JSON response keys: {data.keys()}")
                         # Fallback if binary is in a key?
                        raise Exception("Pixelcut returned no image URL")
                elif "image" in content_type:
                     # Direct image return
                     background_image = Image.open(io.BytesIO(resp.content)).convert("RGBA")
                else:
                    # Try opening as image anyway
                     try:
                        background_image = Image.open(io.BytesIO(resp.content)).convert("RGBA")
                     except:
                        print(f"Pixelcut Unknown Response: {resp.text[:200]}")
                        raise Exception("Pixelcut returned unknown format")

            else:
                 print(f"Pixelcut API error: {resp.status_code} - {resp.text}")
                 # If 400/422, it might be the multipart issue.
                 raise Exception(f"Pixelcut API Error: {resp.status_code}")
            
            # Safe resize background
            background_image = background_image.resize(image_no_bg.size, Image.Resampling.LANCZOS)
            
            # Pixelcut usually returns the COMPOSITED image (product + background).
            # So we might not need to composite ourselves if the input image was the RGBA product.
            # If we composite again, we might double-layer.
            # Let's check: Pixelcut generate-background takes product and PUTS it on background.
            # So the result IS the final image.
            
            final_image = background_image.convert("RGB")
            
            # If we manually composited, we'd do this:
            # final_image = Image.alpha_composite(background_image, image_no_bg)
            # But for Pixelcut, let's assume it returns final. 
            # If it returns JUST background (rare for such APIs), we'd know.
            # Usually "Generate Background" implies placing the product.
            
        except Exception as e:
            print(f"Background generation failed: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to white background
            background = Image.new("RGBA", image_no_bg.size, (255, 255, 255, 255))
            final_image = Image.alpha_composite(background, image_no_bg)
            final_image = final_image.convert("RGB")

        # Convert processed image to base64
        processed_image_b64 = image_to_base64(final_image, "JPEG")
        
        # Step 5: Extract keywords and calculate price
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
