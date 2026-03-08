# Import required libraries
import streamlit as st  # for creating the web app
from dotenv import load_dotenv  # for loading API key from .env file
import os
import json
import google.generativeai as genai  # Google's AI model
from PIL import Image  # for handling images

# Load the API key from .env file
load_dotenv()

# Set up the Google Gemini AI with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get AI response about the food image
def get_gemini_response(image, prompt):
    """Send image to Google's AI and get calorie information"""
    try:
        model = genai.GenerativeModel('gemini-3.1-flash-image-preview')
        response = model.generate_content([image[0], prompt])
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Function to prepare the uploaded image for AI processing
def prepare_image(uploaded_file):
    """Convert uploaded image to format required by Google's AI"""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        return None

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
                image_data = prepare_image(uploaded_file)
                if image_data is not None:
                    response = get_gemini_response(image_data, prompt)

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
