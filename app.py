# Import required libraries
import streamlit as st  # for creating the web app
from dotenv import load_dotenv  # for loading API key from .env file
import os
import json
import io
import google.generativeai as genai  # Google's AI model
from PIL import Image  # for handling images

# Load the API key from .env file
load_dotenv()

# Set up the Google Gemini AI with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Cache model initialization so it's created once per session
@st.cache_resource
def get_model():
    return genai.GenerativeModel('gemini-3.1-flash-image-preview')

# Function to get AI response about the food image
# Cache results so the same image isn't re-analyzed on every rerun
@st.cache_data(show_spinner=False)
def get_gemini_response(image_bytes, prompt):
    """Send image to Google's AI and get calorie information"""
    try:
        model = get_model()
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}
        response = model.generate_content([image_part, prompt])
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
    # Set up the webpage
    st.set_page_config(page_title="Calorie Advisor", page_icon="🍽️")

    # Add title and description
    st.title("🍽️ Calorie Advisor")
    st.write("Upload a photo of your food to get calorie information!")

    # Create file uploader
    uploaded_file = st.file_uploader(
        "Upload your food image (jpg, jpeg, or png)",
        type=["jpg", "jpeg", "png"]
    )

    # Display uploaded image
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Your Food Image", width=700)

        # Create Analyze button
        if st.button("Calculate Calories"):
            with st.spinner("Analyzing your food..."):
                # Prepare the prompt for AI
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

                # Get AI response
                image_bytes = prepare_image(uploaded_file)
                if image_bytes is not None:
                    response = get_gemini_response(image_bytes, prompt)

                    # Try to parse as JSON for rich display
                    try:
                        # Strip markdown code fences if present
                        clean = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
                        data = json.loads(clean)

                        st.success("Analysis Complete!")

                        # Dish description
                        st.info(data.get("description", ""))

                        # Food items table with macros
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

                        # Total calories metric
                        st.metric(label="Total Calories", value=f"{data.get('total_calories', 0)} kcal")

                        # Health tips
                        st.subheader("Health Tips")
                        for tip in data.get("health_tips", []):
                            st.success(tip)

                    except (json.JSONDecodeError, KeyError):
                        # Fallback to plain text if JSON parsing fails
                        st.success("Analysis Complete!")
                        st.write(response)
                else:
                    st.error("Please upload an image first!")

# Run the app
if __name__ == "__main__":
    main()
