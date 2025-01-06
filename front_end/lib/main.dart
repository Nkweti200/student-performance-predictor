import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Student Performance Predictor',
      home: PredictorPage(),
    );
  }
}

class PredictorPage extends StatefulWidget {
  @override
  _PredictorPageState createState() => _PredictorPageState();
}

class _PredictorPageState extends State<PredictorPage> {
  final TextEditingController g1Controller = TextEditingController();
  final TextEditingController g2Controller = TextEditingController();
  final TextEditingController studytimeController = TextEditingController();
  final TextEditingController absencesController = TextEditingController();
  final TextEditingController avgGradeController = TextEditingController();

  String? prediction;

  Future<void> getPrediction() async {
    final url =
        Uri.parse('http://127.0.0.1:8000/api/predict/'); // Django API URL

    try {
      // Prepare input data
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'G1': double.parse(g1Controller.text),
          'G2': double.parse(g2Controller.text),
          'studytime': double.parse(studytimeController.text),
          'absences': double.parse(absencesController.text),
          'avg_grade': double.parse(avgGradeController.text),
        }),
      );

      // Handle the response
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          prediction = 'Predicted Grade: ${data['prediction']}';
        });
      } else {
        setState(() {
          prediction = 'Error: ${response.body}';
        });
      }
    } catch (e) {
      setState(() {
        prediction = 'Error: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Student Performance Predictor')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: g1Controller,
              decoration: InputDecoration(labelText: 'Grade 1 (G1)'),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: g2Controller,
              decoration: InputDecoration(labelText: 'Grade 2 (G2)'),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: studytimeController,
              decoration: InputDecoration(labelText: 'Study Time (hours)'),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: absencesController,
              decoration: InputDecoration(labelText: 'Absences'),
              keyboardType: TextInputType.number,
            ),
            TextField(
              controller: avgGradeController,
              decoration: InputDecoration(labelText: 'Average Grade'),
              keyboardType: TextInputType.number,
            ),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: getPrediction,
              child: Text('Get Prediction'),
            ),
            SizedBox(height: 16),
            if (prediction != null)
              Text(prediction!, style: TextStyle(fontSize: 18)),
          ],
        ),
      ),
    );
  }
}
