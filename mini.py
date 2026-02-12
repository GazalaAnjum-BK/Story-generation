import streamlit as st
from transformers import pipeline, set_seed
import base64
from io import BytesIO

# -----------------------------------------------------
# 1️⃣ Page Setup with Background
# -----------------------------------------------------
st.set_page_config(page_title="AI Story Continuation", page_icon="✨", layout="centered")

# Set light blue background
def set_light_blue_background():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%, #90caf9 100%);
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Add overlay for better readability */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.85);
        z-index: -1;
    }
    
    /* Style main containers */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
    }
    
    /* Style headers */
    h1, h2, h3 {
        color: #2c3e50 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }
    
    /* Style buttons */
    .stButton button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px 0 rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 20px 0 rgba(0,0,0,0.3) !important;
    }
    
    /* Style text areas */
    .stTextArea textarea {
        border-radius: 15px !important;
        border: 2px solid #e0e0e0 !important;
        background: rgba(255,255,255,0.9) !important;
    }
    
    /* Style select boxes */
    .stSelectbox select {
        border-radius: 15px !important;
        background: rgba(255,255,255,0.9) !important;
    }
    
    /* Style sliders */
    .stSlider {
        padding: 10px 0;
    }
    
    /* Download button specific styling */
    .stDownloadButton button {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Apply the background
set_light_blue_background()

st.title("🎨📖 AI Story Continuation Generator")
st.write("Enhanced with beautiful light blue background!")

# -----------------------------------------------------
# 2️⃣ Load the Model
# -----------------------------------------------------
@st.cache_resource
def load_model():
    try:
        # Using GPT-Neo-125M for better story coherence
        return pipeline("text-generation", model="EleutherAI/gpt-neo-125M")
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

generator = load_model()
if generator:
    set_seed(42)

# -----------------------------------------------------
# 3️⃣ Enhanced Story Generation Function
# -----------------------------------------------------
def generate_story(theme, prompt, max_words, character_name):
    """
    Generates highly relevant, theme-consistent story continuation with improved prompting.
    """
    
    # Enhanced theme instructions with more specific guidance
    theme_instruction = {
        "Horror": "Continue the story in a chilling, suspenseful manner. Build atmosphere, create tension, and introduce elements of fear or the unknown. Focus on sensory details that evoke dread.",
        "Fantasy": "Continue the story with vivid descriptions of magical elements, mythical creatures, or extraordinary settings. Develop the character's journey and include elements of wonder and adventure.",
        "Romance": "Continue the story with emotional depth, meaningful interactions, and developing relationships. Focus on feelings, subtle gestures, and meaningful dialogue.",
        "Mystery": "Continue the story by introducing clues, red herrings, or suspicious characters. Build intrigue and move the investigation forward while maintaining suspense.",
        "Sci-Fi": "Continue the story by exploring futuristic technology, alien environments, or scientific concepts. Consider the implications on society and characters."
    }

    instruction = theme_instruction.get(theme, "Continue the story coherently and creatively, maintaining the established tone and style.")
    
    # Calculate max_length more accurately
    max_length_tokens = min(int(max_words * 1.8), 1024)  # Cap at model limit
    
    # Enhanced prompt structure
    name_context = f"The main character is {character_name}. " if character_name else ""
    
    # More natural, story-focused prompt
    combined_prompt = (
        f"Write a compelling continuation of this {theme.lower()} story. {instruction}\n\n"
        f"{name_context}"
        f"Story beginning: \"{prompt}\"\n\n"
        f"Story continuation:"
    )

    try:
        story = generator(
            combined_prompt,
            max_length=max_length_tokens,
            temperature=0.85,  # Balanced creativity and coherence
            top_p=0.92,
            repetition_penalty=1.3,
            do_sample=True,
            num_return_sequences=1,
            pad_token_id=generator.tokenizer.eos_token_id,
            truncation=True
        )[0]['generated_text']

        # Improved text cleaning
        if "Story continuation:" in story:
            story = story.split("Story continuation:")[-1].strip()
        elif "story continuation:" in story:
            story = story.split("story continuation:")[-1].strip()
        
        # Remove any remaining prompt fragments
        cleanup_phrases = [
            "Write a compelling continuation",
            "Story beginning:",
            "story beginning:",
            f"\"{prompt}\""
        ]
        
        for phrase in cleanup_phrases:
            if phrase in story:
                story = story.split(phrase)[-1].strip()

        # Final cleanup
        story = story.strip()
        story = story.lstrip('"').lstrip("'").strip()
        
        # Ensure the story starts properly
        if not story or len(story.split()) < 10:
            return "The story generation didn't produce sufficient content. Please try again with a different prompt."
            
        return story
        
    except Exception as e:
        return f"Error generating story: {str(e)}"

# -----------------------------------------------------
# 4️⃣ Streamlit User Interface
# -----------------------------------------------------

# Header with theme-based color
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin: 20px 0;">
    <h1 style="color: white; margin: 0;">✨ Magic Story Weaver ✨</h1>
    <p style="color: white; opacity: 0.9; margin: 5px 0 0 0;">Create amazing stories with AI!</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 🎭 Set the Stage and the Hero")

col1, col2 = st.columns([2, 1])

with col1:
    theme = st.selectbox("Select a theme:", ["Horror", "Fantasy", "Romance", "Mystery", "Sci-Fi"])
    
with col2:
    max_words = st.slider("Max Story Length (Words):", min_value=100, max_value=500, value=250, step=50)

character_name = st.text_input("Main Character's Name (Optional):", placeholder="e.g., Elara, Detective Kaito, Jane Doe")

# Enhanced prompt guidance with theme-based styling
theme_colors = {
    "Horror": "#ff6b6b",
    "Fantasy": "#4ecdc4", 
    "Romance": "#ff9ff3",
    "Mystery": "#54a0ff",
    "Sci-Fi": "#48dbfb"
}

theme_color = theme_colors.get(theme, "#4ecdc4")

st.markdown(f"""
<div style="background: linear-gradient(135deg, {theme_color}20, #ffffff); padding: 20px; border-radius: 15px; border-left: 5px solid {theme_color}; margin: 20px 0;">
    <h4 style="color: {theme_color}; margin-top: 0;">💡 Writing Tips for {theme} Stories</h4>
    <small>
    <strong>For {theme}:</strong> {
        "Create suspense with eerie settings and unexpected sounds" if theme == "Horror" else
        "Build magical worlds with unique creatures and ancient prophecies" if theme == "Fantasy" else
        "Focus on emotional moments and meaningful connections" if theme == "Romance" else
        "Plant clever clues and introduce suspicious characters" if theme == "Mystery" else
        "Imagine futuristic technology and its impact on humanity"
    }<br><br>
    <strong>Example:</strong> {
        "'The old house creaked with every step, but this time the sound came from the basement...'" if theme == "Horror" else
        "'As Elara touched the ancient rune, the stone doorway began to glow with ethereal light...'" if theme == "Fantasy" else
        "'Their eyes met across the crowded room, and in that moment, nothing else mattered...'" if theme == "Romance" else
        "'The detective noticed the broken clock - stopped at exactly 2:17 AM, the time of the murder...'" if theme == "Mystery" else
        "'The alien artifact hummed with energy, displaying star maps of unknown galaxies...'"
    }
    </small>
</div>
""", unsafe_allow_html=True)

user_input = st.text_area("Enter the beginning of your story:", height=150, 
                         placeholder="Write your story beginning here...\n\nExample: 'The rain fell in sheets as Detective Kaito stepped into the dimly lit alley. The case had gone cold months ago, but this new clue changed everything.'")

# Generation parameters
with st.expander("🎛 Advanced Story Settings"):
    col3, col4 = st.columns(2)
    with col3:
        creativity = st.slider("Creativity Level", 0.1, 1.0, 0.85, 
                              help="Higher values make the story more creative but less predictable")
    with col4:
        show_prompt = st.checkbox("Show generation details", help="Display technical details about the generation process")

# Generate button with special styling
st.markdown("<br>", unsafe_allow_html=True)
col5, col6, col7 = st.columns([1, 2, 1])
with col6:
    generate_clicked = st.button("🪄 view the Story! 🪄", type="primary", use_container_width=True)

if generate_clicked:
    if user_input.strip():
        if not generator:
            st.error("Model failed to load. Please refresh the page and try again.")
        else:
            with st.spinner(f"✨ Weaving your {theme.lower()} tale... This may take a moment."):
                # Update generator parameters based on creativity slider
                story = generate_story(theme, user_input, max_words, character_name)
            
            if story.startswith("Error"):
                st.error(story)
            else:
                st.markdown("---")
                st.subheader("📖 Your Magical Story Continues...")
                
                # Story metadata with themed styling
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {theme_color}20, #ffffff); padding: 15px; border-radius: 10px; margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div><strong>🎭 Theme:</strong> {theme}</div>
                        <div><strong>👤 Character:</strong> {character_name or 'Unnamed Hero'}</div>
                        <div><strong>📏 Length:</strong> {len(story.split())} words</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display story in a beautiful container
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 30px;
                    border-radius: 20px;
                    border-left: 8px solid {theme_color};
                    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                    margin: 25px 0;
                    line-height: 1.8;
                    font-size: 17px;
                    font-family: 'Georgia', serif;
                    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                ">
                {story}
                </div>
                """, unsafe_allow_html=True)
                
                # Download button
                st.download_button(
                    "💾 Download Your Story", 
                    story, 
                    file_name=f"{theme.lower()}story{character_name or 'unknown'}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
                
                # Show generation details if requested
                if show_prompt:
                    with st.expander("🔧 Generation Details"):
                        st.write(f"Model: GPT-Neo-125M")
                        st.write(f"Creativity Level: {creativity}")
                        st.write(f"Max Tokens: {min(int(max_words * 1.8), 1024)}")
                        theme_instructions = {
                            "Horror": "Continue the story in a chilling, suspenseful manner...",
                            "Fantasy": "Continue the story with vivid descriptions of magical elements...",
                            "Romance": "Continue the story with emotional depth...",
                            "Mystery": "Continue the story by introducing clues...",
                            "Sci-Fi": "Continue the story by exploring futuristic technology..."
                        }
                        st.write(f"Theme Guidance: {theme_instructions.get(theme, 'Default')}")
    else:
        st.warning("Please enter a story beginning to continue.")

# -----------------------------------------------------
# 5️⃣ Footer with Enhanced Styling
# -----------------------------------------------------
st.markdown("---")
st.markdown(f"""
<div style="
    text-align: center; 
    padding: 30px; 
    background: linear-gradient(135deg, {theme_color}10, #ffffff);
    border-radius: 20px;
    margin: 20px 0;
">
    <h4 style="color: {theme_color}; margin-bottom: 15px;">🌟 Tips for Magical Stories</h4>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; text-align: left;">
        <div>
            <strong>🎯 Character Development</strong><br>
            <small>• Give your characters unique personalities<br>• Show their emotions through actions</small>
        </div>
        <div>
            <strong>🌍 World Building</strong><br>
            <small>• Use sensory details (sights, sounds, smells)<br>• Create immersive environments</small>
        </div>
        <div>
            <strong>📖 Story Structure</strong><br>
            <small>• Establish clear conflict early<br>• Build tension toward a climax</small>
        </div>
    </div>
    <div style="margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.7); border-radius: 10px;">
        <small>Story crafted with ❤ by Magic Story Weaver</small>
    </div>
</div>
""", unsafe_allow_html=True)