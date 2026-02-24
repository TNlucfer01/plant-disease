import 'dart:io';
import 'dart:math';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'package:image/image.dart' as img;
import 'package:onnxruntime/onnxruntime.dart';

void main() {
  runApp(const PlantDiseaseApp());
}

class PlantDiseaseApp extends StatelessWidget {
  const PlantDiseaseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Plant Disease Detector',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  File? _image;
  String? _result;
  bool _isProcessing = false;
  OrtSession? _session;

  static const List<String> CLASS_NAMES = [
    'Apple Scab', 'Apple Black Rot', 'Apple Cedar Rust', 'Apple Healthy',
    'Blueberry Healthy', 'Cherry Powdery Mildew', 'Cherry Healthy',
    'Corn Gray Leaf Spot', 'Corn Common Rust', 'Corn Northern Leaf Blight', 'Corn Healthy',
    'Grape Black Rot', 'Grape Esca', 'Grape Leaf Blight', 'Grape Healthy',
    'Orange Haunglongbing', 'Peach Bacterial Spot', 'Peach Healthy',
    'Pepper Bell Bacterial Spot', 'Pepper Bell Healthy', 'Potato Early Blight',
    'Potato Late Blight', 'Potato Healthy', 'Raspberry Healthy', 'Soybean Healthy',
    'Squash Powdery Mildew', 'Strawberry Leaf Scorch', 'Strawberry Healthy',
    'Tomato Bacterial Spot', 'Tomato Early Blight', 'Tomato Late Blight',
    'Tomato Leaf Mold', 'Tomato Septoria Leaf Spot', 'Tomato Spider Mites',
    'Tomato Target Spot', 'Tomato Yellow Leaf Curl Virus', 'Tomato Mosaic Virus',
    'Tomato Healthy',
  ];

  @override
  void initState() {
    super.initState();
    _initModel();
  }

  Future<void> _initModel() async {
    try {
      OrtEnv.instance.init();
      final rawModelPath = 'assets/plant_disease_model.onnx';
      final modelData = await rootBundle.load(rawModelPath);
      final modelBytes = modelData.buffer.asUint8List();

      final env = OrtEnv.instance;
      final sessionOptions = OrtSessionOptions();
      _session = OrtSession.fromBuffer(modelBytes, sessionOptions);
    } catch (e) {
      debugPrint("Error loading model: $e");
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: source);

    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
        _result = null;
      });
      _predict();
    }
  }

  Future<void> _predict() async {
    if (_image == null || _session == null) return;

    setState(() {
      _isProcessing = true;
    });

    try {
      // 1. Preprocess: Resize(256) -> CenterCrop(224) -> Normalize
      final imageBytes = await _image!.readAsBytes();
      img.Image? originalImage = img.decodeImage(imageBytes);
      if (originalImage == null) throw Exception("Could not decode image");

      // Resize shortest side to 256
      int width = originalImage.width;
      int height = originalImage.height;
      int newWidth, newHeight;
      if (width < height) {
        newWidth = 256;
        newHeight = (height * (256 / width)).toInt();
      } else {
        newHeight = 256;
        newWidth = (width * (256 / height)).toInt();
      }
      img.Image resizedImage = img.copyResize(originalImage, width: newWidth, height: newHeight);

      // Center Crop 224
      int x = (newWidth - 224) ~/ 2;
      int y = (newHeight - 224) ~/ 2;
      img.Image croppedImage = img.copyCrop(resizedImage, x: x, y: y, width: 224, height: 224);

      // To Float Array (1, 3, 224, 224) and Normalize
      final mean = [0.485, 0.456, 0.406];
      final std = [0.229, 0.224, 0.225];
      
      final input = Float32List(1 * 3 * 224 * 224);
      for (int i = 0; i < 224; i++) {
        for (int j = 0; j < 224; j++) {
          final pixel = croppedImage.getPixel(j, i);
          // ONNX expects NCHW format
          // R
          input[0 * 224 * 224 + i * 224 + j] = (pixel.r / 255.0 - mean[0]) / std[0];
          // G
          input[1 * 224 * 224 + i * 224 + j] = (pixel.g / 255.0 - mean[1]) / std[1];
          // B
          input[2 * 224 * 224 + i * 224 + j] = (pixel.b / 255.0 - mean[2]) / std[2];
        }
      }

      final shape = [1, 3, 224, 224];
      final inputTensor = OrtValueTensor.createTensorWithDataList(input, shape);
      final Map<String, OrtValue> inputs = {'input': inputTensor};

      final runOptions = OrtRunOptions();
      final outputs = _session!.run(runOptions, inputs);
      
      final outputValue = outputs[0]?.value as List<List<double>>;
      final logits = outputValue[0];

      // Find max
      double maxLogit = double.negativeInfinity;
      int maxIdx = 0;
      for (int k = 0; k < logits.length; k++) {
        if (logits[k] > maxLogit) {
          maxLogit = logits[k];
          maxIdx = k;
        }
      }

      setState(() {
        _result = CLASS_NAMES[maxIdx];
      });

      inputTensor.release();
      for (var element in outputs) {
        element?.release();
      }
    } catch (e) {
      debugPrint("Prediction error: $e");
      setState(() {
        _result = "Error during prediction";
      });
    } finally {
      setState(() {
        _isProcessing = false;
      });
    }
  }

  @override
  void dispose() {
    _session?.release();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Plant Disease Detector'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            if (_image != null)
              Container(
                width: 300,
                height: 300,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.green, width: 2),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.file(_image!, fit: BoxFit.cover),
                ),
              )
            else
              const Icon(Icons.image, size: 100, color: Colors.grey),
            const SizedBox(height: 20),
            if (_isProcessing)
              const CircularProgressIndicator()
            else if (_result != null)
              Text(
                'Detected: $_result',
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.green),
              )
            else
              const Text('Take a photo of a leaf to begin'),
            const SizedBox(height: 30),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  onPressed: () => _pickImage(ImageSource.camera),
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Camera'),
                ),
                ElevatedButton.icon(
                  onPressed: () => _pickImage(ImageSource.gallery),
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Gallery'),
                ),
              ],
            )
          ],
        ),
      ),
    );
  }
}
