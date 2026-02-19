from plant_disease_cnn import PlantDiseaseCNN

# Load the trained model
model = PlantDiseaseCNN()
model.load_model('best_plant_disease_model.pth')
# Make predictions
result = model.predict('temp_upload.jpg')

print(result)