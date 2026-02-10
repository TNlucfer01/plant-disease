"""
Streamlit App for Plant Disease Detection
Complete UI for CNN → LLM pipeline
"""

import streamlit as st
from PIL import Image
import io
import json
from pathlib import Path
import sys

# Import pipeline
from plant_disease_pipeline import PlantDiseaseAssistant

# Page config
st.set_page_config(
    page_title="Plant Disease Detection",
    page_icon="🌿",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .confidence-high {
        background-color: #C8E6C9;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #4CAF50;
    }
    .confidence-low {
        background-color: #FFECB3;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #FFA726;
    }
    .advice-box {
        background-color: #E3F2FD;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #2196F3;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'assistant' not in st.session_state:
    with st.spinner("Loading AI models..."):
        st.session_state.assistant = PlantDiseaseAssistant(
            num_classes=38,
            confidence_threshold=0.7,
            llm_model="llama3.2:1b"
        )
    st.success("Models loaded successfully!")

# Header
st.markdown('<p class="main-header">🌿 Plant Disease Detection Assistant</p>', 
            unsafe_allow_html=True)
st.markdown("Upload a leaf image to detect diseases and get treatment recommendations")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    confidence_threshold = st.slider(
        "Confidence Threshold",
        min_value=0.5,
        max_value=0.95,
        value=0.7,
        step=0.05,
        help="Minimum confidence level for diagnosis"
    )
    
    st.session_state.assistant.cnn.confidence_threshold = confidence_threshold
    
    st.markdown("---")
    st.subheader("About")
    st.markdown("""
    **Model:** MobileNetV2  
    **LLM:** Ollama (Local)  
    **Classes:** 38 plant diseases  
    
    **Supported Plants:**
    - Apple, Tomato, Potato
    - Corn, Grape, Pepper
    - Strawberry, Cherry, Peach
    - And more...
    """)
    
    st.markdown("---")
    
    # System status
    st.subheader("System Status")
    
    # Check Ollama
    llm_status = st.session_state.assistant.llm.test_connection()
    if llm_status:
        st.success("✓ LLM Connected")
    else:
        st.warning("⚠️ LLM Offline (using fallback)")
    
    # Model info
    with st.expander("Model Details"):
        import torch
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        st.write(f"**Device:** {device}")
        st.write(f"**Threshold:** {confidence_threshold:.0%}")

# Main interface
tab1, tab2, tab3 = st.tabs(["📸 Single Image", "📁 Batch Analysis", "📊 History"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Image")
        uploaded_file = st.file_uploader(
            "Choose a leaf image",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear image of a plant leaf"
        )
        
        if uploaded_file is not None:
            # Display image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Save temporarily
            temp_path = Path("temp_upload.jpg")
            image.save(temp_path)
    
    with col2:
        st.subheader("Analysis Results")
        
        if uploaded_file is not None:
            if st.button("🔍 Analyze", type="primary"):
                with st.spinner("Analyzing image..."):
                    # Run analysis
                    result = st.session_state.assistant.analyze(
                        temp_path, 
                        verbose=False
                    )
                    
                    # Store in session
                    if 'history' not in st.session_state:
                        st.session_state.history = []
                    st.session_state.history.append(result)
                
                # Display detection results
                detection = result['detection']
                
                # Confidence indicator
                if detection['is_confident']:
                    st.markdown(
                        f'<div class="confidence-high">'
                        f'<strong>High Confidence Detection</strong><br>'
                        f'Confidence: {detection["confidence"]:.1%}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="confidence-low">'
                        f'<strong>Low Confidence Detection</strong><br>'
                        f'Confidence: {detection["confidence"]:.1%}<br>'
                        f'⚠️ Further verification recommended'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                
                st.markdown("---")
                
                # Main result
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Plant Type", detection['plant'])
                with col_b:
                    st.metric("Condition", detection['disease'])
                
                # Top predictions
                with st.expander("View Top 5 Predictions"):
                    for i, pred in enumerate(detection['top_5'], 1):
                        st.write(
                            f"**{i}.** {pred['plant']} - {pred['disease']} "
                            f"({pred['confidence']:.1%})"
                        )
    
    # Treatment advice (full width)
    if uploaded_file is not None and 'result' in locals():
        st.markdown("---")
        st.subheader("🌱 Treatment Recommendations")
        
        advice = result['advice']
        
        if advice['success']:
            st.markdown(
                f'<div class="advice-box">{advice["advice"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.error(f"LLM Error: {advice.get('error')}")
            if 'fallback_advice' in advice:
                st.info(advice['fallback_advice'])
        
        # Download results
        st.markdown("---")
        col_download1, col_download2 = st.columns(2)
        
        with col_download1:
            # JSON download
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="📥 Download JSON Report",
                data=json_str,
                file_name="disease_analysis.json",
                mime="application/json"
            )
        
        with col_download2:
            # Text summary download
            summary = f"""PLANT DISEASE ANALYSIS REPORT
{'='*60}

DETECTION:
Plant: {detection['plant']}
Disease: {detection['disease']}
Confidence: {detection['confidence']:.1%}
Status: {'High Confidence' if detection['is_confident'] else 'Low Confidence'}

TOP 5 PREDICTIONS:
"""
            for i, pred in enumerate(detection['top_5'], 1):
                summary += f"{i}. {pred['plant']} - {pred['disease']} ({pred['confidence']:.1%})\n"
            
            summary += f"\n{'='*60}\nTREATMENT ADVICE:\n{'='*60}\n\n"
            if advice['success']:
                summary += advice['advice']
            else:
                summary += advice.get('fallback_advice', 'No advice available')
            
            st.download_button(
                label="📄 Download Text Report",
                data=summary,
                file_name="disease_report.txt",
                mime="text/plain"
            )

with tab2:
    st.subheader("Batch Image Analysis")
    st.info("Upload multiple images for batch processing")
    
    uploaded_files = st.file_uploader(
        "Choose multiple leaf images",
        type=['jpg', 'jpeg', 'png'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} images uploaded**")
        
        if st.button("🔍 Analyze All", type="primary"):
            progress_bar = st.progress(0)
            results_container = st.container()
            
            batch_results = []
            
            for i, file in enumerate(uploaded_files):
                # Update progress
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Save and analyze
                temp_path = Path(f"temp_{i}.jpg")
                image = Image.open(file)
                image.save(temp_path)
                
                result = st.session_state.assistant.analyze(temp_path, verbose=False)
                batch_results.append({
                    'filename': file.name,
                    'result': result
                })
                
                # Clean up
                temp_path.unlink()
            
            # Display results
            with results_container:
                st.success(f"Analyzed {len(uploaded_files)} images!")
                
                for item in batch_results:
                    with st.expander(f"📄 {item['filename']}"):
                        det = item['result']['detection']
                        st.write(f"**Plant:** {det['plant']}")
                        st.write(f"**Disease:** {det['disease']}")
                        st.write(f"**Confidence:** {det['confidence']:.1%}")
            
            # Download batch results
            batch_json = json.dumps(batch_results, indent=2)
            st.download_button(
                label="📥 Download Batch Results",
                data=batch_json,
                file_name="batch_analysis.json",
                mime="application/json"
            )

with tab3:
    st.subheader("Analysis History")
    
    if 'history' in st.session_state and st.session_state.history:
        st.write(f"**Total analyses: {len(st.session_state.history)}**")
        
        for i, result in enumerate(reversed(st.session_state.history), 1):
            det = result['detection']
            
            with st.expander(
                f"Analysis #{len(st.session_state.history) - i + 1}: "
                f"{det['plant']} - {det['disease']} ({det['confidence']:.1%})"
            ):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Plant:** {det['plant']}")
                    st.write(f"**Disease:** {det['disease']}")
                with col2:
                    st.write(f"**Confidence:** {det['confidence']:.1%}")
                    st.write(f"**Status:** {'✓ Confident' if det['is_confident'] else '⚠️ Uncertain'}")
        
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("No analysis history yet. Upload an image to get started!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Plant Disease Detection System | Powered by MobileNetV2 + Ollama</p>
    <p>⚠️ For informational purposes only. Consult agricultural experts for critical decisions.</p>
</div>
""", unsafe_allow_html=True)
