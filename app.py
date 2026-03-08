# Import required libraries
import streamlit as st
from dotenv import load_dotenv
import os
import json
import io
from google import genai
from google.genai import types
from PIL import Image

# Load the API key from .env file
load_dotenv()

# Cache the Gemini client so it's created once per session
@st.cache_resource
def get_client():
    return genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Cache results so the same image isn't re-analyzed on every rerun
@st.cache_data(show_spinner=False)
def get_gemini_response(image_bytes, prompt):
    """Send image to Google's AI and get calorie information"""
    try:
        client = get_client()
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                prompt
            ]
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Function to prepare and compress the uploaded image for AI processing
def prepare_image(uploaded_file):
    """Resize and compress image to reduce upload size and speed up API calls"""
    if uploaded_file is None:
        return None
    img = Image.open(uploaded_file)
    # Resize to max 1024px on longest side
    img.thumbnail((1024, 1024), Image.LANCZOS)
    # Re-encode as JPEG at 85% quality
    buffer = io.BytesIO()
    img.convert("RGB").save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()

# Main web app
def main():
    st.set_page_config(page_title="Calorie Advisor", page_icon="🍽️")
    st.title("🍽️ Calorie Advisor")
    st.write("Upload a photo of your food to get calorie information!")

    uploaded_file = st.file_uploader(
        "Upload your food image (jpg, jpeg, or png)",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Your Food Image", width=700)

        if st.button("Calculate Calories"):
            with st.spinner("Analyzing your food..."):
                prompt = """
                Analyze this food image and return ONLY valid JSON in this exact format, no markdown, no extra text:
                {
                  "description": "Brief description of the dish",
                  "items": [
                    {"name": "Food Item", "calories": 200, "protein_g": 10, "carbs_g": 25, "fat_g": 8}
                  ],
                  "total_calories": 200,
                  "health_tips": ["Tip 1", "Tip 2"]
                }
                """

                image_bytes = prepare_image(uploaded_file)
                if image_bytes is not None:
                    response = get_gemini_response(image_bytes, prompt)

                    try:
                        clean = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                        data = json.loads(clean)

                        st.success("Analysis Complete!")
                        st.info(data.get("description", ""))

                        st.subheader("Food Breakdown")
                        rows = []
                        for item in data.get("items", []):
                            rows.append({
                                "Food Item": item.get("name", ""),
                                "Calories": item.get("calories", 0),
                                "Protein (g)": item.get("protein_g", 0),
                                "Carbs (g)": item.get("carbs_g", 0),
                                "Fat (g)": item.get("fat_g", 0),
                            })
                        st.dataframe(rows, use_container_width=True, hide_index=True)

                        st.metric(label="Total Calories", value=f"{data.get('total_calories', 0)} kcal")

                        st.subheader("Health Tips")
                        for tip in data.get("health_tips", []):
                            st.success(tip)

                    except (json.JSONDecodeError, KeyError):
                        st.success("Analysis Complete!")
                        st.write(response)
                else:
                    st.error("Please upload an image first!")

if __name__ == "__main__":
    main()
