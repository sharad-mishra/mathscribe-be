# apps/calculator/utils.py

import json
import ast
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
from constants import GEMINI_API_KEY
import google.generativeai as genai

def preprocess_image(img: Image) -> Image:
    """
    Preprocess the input image to enhance clarity for better AI interpretation.

    Steps:
    1. Convert to grayscale.
    2. Invert colors to have a white background with black text.
    3. Enhance contrast to make the drawing more prominent.

    Args:
        img (Image): PIL Image object to be preprocessed.

    Returns:
        Image: Preprocessed PIL Image object.
    """
    # Convert to grayscale
    img = img.convert('L')

    # Invert colors (optional based on your drawing background)
    img = ImageOps.invert(img)

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)

    return img

def analyze_image(img: Image, dict_of_vars: dict):
    """
    Analyze the drawn mathematical expression from the provided image using GenAI.

    This function preprocesses the image, generates a prompt combining the image and variables,
    sends it to the GenAI model, parses the response, and returns structured results.

    Args:
        img (Image): PIL Image object containing the drawn mathematical expression.
        dict_of_vars (dict): Dictionary of variables to be used in evaluating the expression.

    Returns:
        list or dict: 
            - On success: List of dictionaries containing 'expr', 'result', and 'assign' keys.
            - On failure: Dictionary with 'message' and 'status' keys indicating the error.
    """
    try:
        # Configure GenAI with the provided API key
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Error configuring GenAI: {e}")
        return {"message": "Internal server error during GenAI configuration.", "status": "error"}

    try:
        # Preprocess the image for better clarity
        img = preprocess_image(img)
        print("Image preprocessed for better clarity.")

        # Initialize the GenAI model
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        # Serialize the variables dictionary to a JSON string
        dict_of_vars_str = json.dumps(dict_of_vars, ensure_ascii=False)

        # Generate the prompt for GenAI
        prompt = f"""
Analyze the following handwritten mathematical expression from the provided image and evaluate it based on the given variables.

Variables: {dict_of_vars_str}

Image: [Please refer to the attached image]

Please provide the expression, the result, and indicate whether it involves an assignment.

Respond in the following JSON format:

[
    {{
        "expr": "expression as string",
        "result": "result as string",
        "assign": true or false
    }},
    ...
]
"""
        print("Generated Prompt:", prompt[:500] + '...')  # Log first 500 characters for brevity

        # Send the prompt and image to the GenAI model
        response = model.generate_content([prompt, img])
        print(f"GenAI Response: {response.text[:500]}...")  # Log first 500 characters for brevity

        answers = []

        try:
            # Clean the response text by removing backticks
            cleaned_response_text = response.text.replace('```json', '').replace('```', '').strip()
            # Parse the cleaned response text into a Python list
            answers = json.loads(cleaned_response_text)
            print("Parsed Answers:", answers)
        except Exception as e:
            print(f"Error parsing GenAI response: {e}")
            return {"message": "Failed to parse AI response.", "status": "error"}

        # Process each answer to ensure the 'assign' flag is present
        for answer in answers:
            if 'assign' not in answer:
                answer['assign'] = False

        print("Final Answers with Assign Flags:", answers)
        return answers

    except Exception as e:
        print(f"Error in analyze_image function: {e}")
        return {"message": "Internal server error during image analysis.", "status": "error"}