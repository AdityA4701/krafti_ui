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
        print(f"Generating background via Pixelcut for prompt: {bg_prompt_text}")
        
        final_image = original_image # Default fallback
        
        try:
            pixelcut_key = os.getenv("PIXELCUT_API_KEY")
            if not pixelcut_key:
                print("Warning: PIXELCUT_API_KEY not found variables.")
                raise Exception("Missing Pixelcut Key")

            # Optimize prompt for Pixelcut - Glassy Reflection
            bg_gen_prompt = f"professional product photography background, on a glassy reflective surface, reflection of the object, glossy, {bg_prompt_text}, soft natural lighting, realistic shadows, high quality, 8k, photorealistic"
            
            print(f"Requesting Pixelcut with prompt: {bg_gen_prompt}")
            
            # Strategy A: Try Pixelcut with 0x0.st hosting
            try:
                # Prepare image buffer
                img_byte_arr = io.BytesIO()
                original_image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)

                print("Uploading to 0x0.st...")
                # 0x0.st is a reliable file dump
                files_io = {"file": ("image.png", img_byte_arr, "image/png")}
                io_resp = requests.post("https://0x0.st", files=files_io)
                
                if io_resp.status_code != 200:
                    raise Exception(f"0x0.st upload failed: {io_resp.text}")
                
                public_img_url = io_resp.text.strip()
                print(f"Public URL: {public_img_url}")

                url = "https://api.developer.pixelcut.ai/v1/generate-background"
                
                payload = {
                    "image_url": public_img_url,
                    "prompt": bg_gen_prompt,
                    "format": "jpeg"
                }
                headers = {
                    "X-API-KEY": pixelcut_key,
                    "Content-Type": "application/json"
                }
                
                resp = requests.post(url, headers=headers, json=payload)
                
                if resp.status_code == 200:
                    content_type = resp.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        data = resp.json()
                        if "result_url" in data:
                            img_resp = requests.get(data["result_url"])
                            final_image = Image.open(io.BytesIO(img_resp.content)).convert("RGB")
                        else:
                            raise Exception("No URL in Pixelcut JSON")
                    elif "image" in content_type:
                        final_image = Image.open(io.BytesIO(resp.content)).convert("RGB")
                    else:
                        raise Exception("Unknown Pixelcut response type")
                else:
                    raise Exception(f"Pixelcut API Error: {resp.status_code} {resp.text}")

            except Exception as e_pixel:
                print(f"Strategy A (Pixelcut) failed: {e_pixel}")
                print("Switching to Strategy B: Remove.bg + White Background")
                
                # Strategy B: Remove BG + White Background
                # This ensures the user ALWAYS gets a result
                try:
                    img_byte_arr.seek(0)
                    no_bg_bytes = remove_background_api(img_byte_arr.getvalue())
                    no_bg_image = Image.open(io.BytesIO(no_bg_bytes)).convert("RGBA")
                    
                    # Create white background
                    white_bg = Image.new("RGBA", no_bg_image.size, "WHITE")
                    final_image = Image.alpha_composite(white_bg, no_bg_image).convert("RGB")
                    
                    # Append note to description
                    description += " (Note: Standard white background applied due to high traffic.)"
                except Exception as e_fallback:
                    raise HTTPException(status_code=500, detail=f"All strategies failed. Pixelcut: {e_pixel}, Fallback: {e_fallback}")



        except Exception as e:
            # Re-raise exceptions from inner strategies (including the traceback)
            raise e

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
