import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(MovieApp());
}

class MovieApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Movie Recommender',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: MovieScreen(),
    );
  }
}

class MovieScreen extends StatefulWidget {
  @override
  _MovieScreenState createState() => _MovieScreenState();
}

class _MovieScreenState extends State<MovieScreen> {
  final TextEditingController _controller = TextEditingController();
  List<dynamic> recommendations = [];
  bool isLoading = false;

  Future<void> fetchRecommendations(String movieName) async {
    setState(() => isLoading = true);

    final url = Uri.parse("http://192.168.1.7:5000/recommend"); 
    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"movie": movieName}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      setState(() {
        recommendations = data['recommendations'];
        isLoading = false;
      });
    } else {
      setState(() => isLoading = false);
      throw Exception("Failed to load recommendations");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Movie Recommender")),
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [
            TextField(
              controller: _controller,
              decoration: InputDecoration(
                hintText: "Enter a movie name",
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 10),
            ElevatedButton(
              onPressed: () {
                if (_controller.text.isNotEmpty) {
                  fetchRecommendations(_controller.text);
                }
              },
              child: Text("Recommend"),
            ),
            SizedBox(height: 20),
            isLoading
                ? CircularProgressIndicator()
                : Expanded(
                    child: GridView.builder(
                      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        childAspectRatio: 0.65,
                        crossAxisSpacing: 10,
                        mainAxisSpacing: 10,
                      ),
                      itemCount: recommendations.length,
                      itemBuilder: (context, index) {
                        final movie = recommendations[index];
                        return Column(
                          children: [
                            Expanded(
                              child: Image.network(
                                movie['poster'] ??
                                    "https://imgs.search.brave.com/MVs_TQ7UIbmuD1zzNHKr2TXcRR8-yBW4UN1tIvQiklw/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9jZG4u/cGl4YWJheS5jb20v/cGhvdG8vMjAyNC8w/Ni8yMi8xNi81NS9h/aS1nZW5lcmF0ZWQt/ODg0NjY3Ml82NDAu/anBn",
                                fit: BoxFit.cover,
                              ),
                            ),
                            SizedBox(height: 5),
                            Text(
                              movie['title'],
                              textAlign: TextAlign.center,
                              style: TextStyle(fontSize: 14),
                            ),
                          ],
                        );
                      },
                    ),
                  ),
          ],
        ),
      ),
    );
  }
}
