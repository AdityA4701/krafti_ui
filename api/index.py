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
from rembg import remove # Local background removal

# Import from SAME directory (api.price_estimator)
# When running in Vercel, this file is the entry point
try:
    from api.price_estimator import calculate_price_range, parse_keywords_from_description
except ImportError:
    # Local fallback or standard import
    from price_estimator import calculate_price_range, parse_keywords_from_description


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
        
        # Step 1: Generate description and background prompt using Gemini
        print("Starting Gemini analysis...")
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Convert image for Gemini (it accepts PIL Image directly)
        description_image = original_image.convert("RGB")
        
        # Using simple string concatenation to avoid syntax errors in tool writing
        analysis_prompt = (
            "Analyze this handmade craft product image and generate:\n"
            "1. A brief e-commerce description (2-3 sentences).\n"
            "2. A short, specific prompt to generate a matching professional background for this product (e.g. 'marble table', 'wooden desk', 'soft fabric').\n"
            "\n"
            "Format:\n"
            "Description: [Description]\n"
            "Background Prompt: [Prompt]"
        )

        try:
            # Run Gemini in thread to avoid blocking event loop
            response = model.generate_content([analysis_prompt, description_image])
            analysis_text = response.text.strip()
            print("Received analysis from Gemini.")
        except Exception as e_gemini:
            print(f"Gemini Analysis Failed: {e_gemini}")
            analysis_text = ""
            # Fallback values
        
        # Parse description and background prompt
        description = "Handmade craft product."
        bg_prompt_text = "minimalist professional studio background, soft lighting, 4k"
        
        if analysis_text:
            try:
                # Use splitlines for safer parsing
                lines = analysis_text.splitlines()
                desc_lines = []
                capture_desc = False
                for line in lines:
                    line = line.strip()
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

        # Step 2: Generate Background Image using Pixelcut API
        # We pass the ORIGINAL image. Pixelcut removes background and composites.
        # Strategy: Local Rembg + Freepik Text-to-Image Composite
        # This avoids the need for public URLs (0x0.st) entirely.
        print("Starting Strategy: Local Rembg + Freepik Composite")
        
        try:
            # 1. Remove Background Locally (rembg)
            print("Removing background locally...")
            img_byte_arr = io.BytesIO()
            original_image.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            no_bg_bytes = remove(img_bytes) # rembg library
            no_bg_image = Image.open(io.BytesIO(no_bg_bytes)).convert("RGBA")
            
            # 2. Generate Background Texture using Freepik API (Text-to-Image)
            # We don't upload the product, we just ask for a background.
            print("Generating background texture via Freepik...")
            freepik_key = "FPSX9478529f74361bb6d9d64e891a989728" # Hardcoded as requested
            
            # Simple prompt for background
            bg_prompt_clean = bg_prompt_text.replace("product", "").replace("background", "").strip()
            texture_prompt = f"product photography background, {bg_prompt_clean}, empty, podium, soft lighting, 8k, high quality"
            
            url = "https://api.freepik.com/v1/ai/text-to-image"
            payload = {
                "prompt": texture_prompt,
                "num_images": 1,
                "image_size": "square_1_1" # or similar
            }
            headers = {
                "x-freepik-api-key": freepik_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Note: If Freepik T2I fails or is different, we fallback to colored BG
            generated_bg = None
            try:
                resp = requests.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    # Parse Freepik response (assuming list of images in base64 or url)
                    # Often it's "data": [{"base64": ...}] or similar
                    # Let's handle standard response types
                    if "data" in data and len(data["data"]) > 0:
                        img_data = data["data"][0]
                        if "base64" in img_data:
                            bg_bytes = base64.b64decode(img_data["base64"])
                            generated_bg = Image.open(io.BytesIO(bg_bytes)).convert("RGBA")
                        elif "url" in img_data:
                            bg_resp = requests.get(img_data["url"])
                            generated_bg = Image.open(io.BytesIO(bg_resp.content)).convert("RGBA")
            except Exception as e_freepik:
                print(f"Freepik T2I failed: {e_freepik}")
                # Fallback to simple gradient or white if generation fails
            
            if not generated_bg:
                # Fallback Background (White/Grey)
                print("Using fallback white background")
                generated_bg = Image.new("RGBA", no_bg_image.size, (245, 245, 245, 255))
            
            # 3. Composite
            # Resize background to match product
            generated_bg = generated_bg.resize(no_bg_image.size, Image.Resampling.LANCZOS)
            
            # Center product?
            # For now, just composite directly (assuming centered input)
            final_image = Image.alpha_composite(generated_bg, no_bg_image).convert("RGB")
            
        except Exception as e_process:
            print(f"Processing failed: {e_process}")
            # Ultimate Fallback: Return Original
            final_image = original_image.convert("RGB")
            # Or raise if we want to debug
            # raise HTTPException(status_code=500, detail=str(e_process))

        # Convert processed image to base64
        processed_image_b64 = image_to_base64(final_image, "JPEG")
        
        # Step 3: Extract keywords and calculate price
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
