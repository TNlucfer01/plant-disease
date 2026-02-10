from plant_disease_pipeline import PlantDiseaseAssistant

# Initialize
assistant = PlantDiseaseAssistant(
    num_classes=38,
    confidence_threshold=0.7,
    llm_model="llama3.2:1b"
)

# Analyze single image
result = assistant.analyze_and_display('temp_upload.jpg')

# Batch analysis
results = assistant.batch_analyze('images_folder/')