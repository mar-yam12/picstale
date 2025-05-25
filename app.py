import streamlit as st
from PIL import Image
import requests
import uuid
import os
import random
import json
from gtts import gTTS

# -------- Hugging Face API Setup --------
HF_TOKEN = "hf_your_huggingface_token_here"  # Replace with your token
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# -------- Classes --------
class ImageCaptioner:
    def __init__(self, image_path):
        self.image_path = image_path
        self.api_url = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"

    def get_caption(self):
        with open(self.image_path, "rb") as f:
            img_bytes = f.read()
        response = requests.post(self.api_url, headers=HEADERS, data=img_bytes)
        if response.status_code == 200:
            return response.json()[0]['generated_text']
        else:
            return "A mysterious image."

class StoryGenerator:
    def __init__(self, prompt):
        self.prompt = prompt
        self.api_url = "https://api-inference.huggingface.co/models/gpt2"

    def generate_story(self):
        payload = {
            "inputs": self.prompt,
            "parameters": {"max_new_tokens": 80, "do_sample": True, "top_k": 50}
        }
        response = requests.post(self.api_url, headers=HEADERS, json=payload)
        if response.status_code == 200:
            story = response.json()[0]['generated_text']
            return story[len(self.prompt):].strip()
        else:
            return None

    def get_random_backup_story(self):
        try:
            with open("stories.json", "r", encoding="utf-8") as f:
                stories = json.load(f)
            return random.choice(stories)
        except:
            return "Once upon a time, a beautiful mystery unfolded under the stars."

class VoiceNarrator:
    def __init__(self, text, lang="en"):
        self.text = text
        self.lang = lang

    def generate_audio(self, filename="story.mp3"):
        tts = gTTS(text=self.text, lang=self.lang)
        tts.save(filename)
        return filename

# -------- Streamlit App --------
def main():
    st.set_page_config(page_title="📸 PicTales", layout="centered")
    st.title("📸 PicTales - Turn Any Picture into a Story")

    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        os.makedirs("uploads", exist_ok=True)
        image = Image.open(uploaded_file)
        img_path = f"uploads/{uuid.uuid4()}.jpg"
        image.save(img_path)

        st.image(image, caption="Uploaded Image", use_container_width=True)

        st.info("Analyzing image for caption...")
        caption = ImageCaptioner(img_path).get_caption()
        st.success(f"Caption: {caption}")

        st.info("Generating a story from the caption...")
        story_gen = StoryGenerator(prompt=caption)
        story = story_gen.generate_story()
        if not story:
            story = story_gen.get_random_backup_story()
            st.warning("Using a random story from backup.")

        st.subheader("📖 Your Story")
        st.write(story)

        st.info("Creating audio narration...")
        audio_file = VoiceNarrator(story).generate_audio()
        st.audio(audio_file)

if __name__ == "__main__":
    main()
