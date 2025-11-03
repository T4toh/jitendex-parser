
# Jitendex Parser

This project provides a script to parse the Jitendex dictionary data and create a SQLite database for use in a Flutter application.

## What's in this repository?

*   `parser.py`: A Python script that parses the raw Jitendex data and creates the `jitendex.db` database.
*   `jitendex.db`: A pre-built SQLite database containing the parsed dictionary data. You can use this directly in your Flutter app without running the parser script.
*   `README.md`: This file, which provides instructions on how to use the database and the parser script.
*   `.gitignore`: A file that tells Git to ignore the `jitendex.db` file, as it is a generated file.
*   `verify_db.py`: A Python script to verify the integrity of the database.

## Getting Started

There are two ways to use this project:

**1. Use the pre-built database (Recommended for most users)**

If you just want to use the dictionary data in your Flutter app, you can use the included `jitendex.db` file directly. Follow the instructions in the "How to Use" section below.

**2. Run the parser script yourself**

If you want to modify the parsing logic or use a different version of the Jitendex data, you can run the `parser.py` script. Here's how:

1.  **Download the data:** Download the "Jitendex for Yomitan" file from the [Jitendex downloads page](https://jitendex.org/pages/downloads.html).
2.  **Unzip the data:** Unzip the downloaded file. This will create a number of `term_bank_*.json` files.
3.  **Place the data:** Move the `term_bank_*.json` files into the root of this repository.
4.  **Run the script:** Run the following command in your terminal:

    ```bash
    python parser.py
    ```

    This will create a new `jitendex.db` file.

## How to Use the Database in a Flutter App

1.  **Add the database to your Flutter project:**

    *   Copy the `jitendex.db` file to your Flutter project's `assets` folder. You may need to create this folder if it doesn't exist.
    *   Add the following to your `pubspec.yaml` file to include the database in your app's assets:

    ```yaml
    flutter:
      assets:
        - assets/jitendex.db
    ```

2.  **Add the `sqflite` package to your project:**

    *   Run the following command in your terminal:

    ```bash
    flutter pub add sqflite
    ```

3.  **Query the database in your Flutter app:**

    *   Here is an example of how to open the database and query for a term:

    ```dart
    import 'package:flutter/services.dart' show rootBundle;
    import 'dart:io';
    import 'package:path/path.dart';
    import 'package:sqflite/sqflite.dart';

    Future<Database> getDatabase() async {
      var databasesPath = await getDatabasesPath();
      var path = join(databasesPath, "jitendex.db");

      // Check if the database exists
      var exists = await databaseExists(path);

      if (!exists) {
        // Should happen only the first time you launch your application
        print("Creating new copy from asset");

        // Make sure the parent directory exists
        try {
          await Directory(dirname(path)).create(recursive: true);
        } catch (_) {}

        // Copy from asset
        ByteData data = await rootBundle.load(join("assets", "jitendex.db"));
        List<int> bytes = data.buffer.asUint8List(data.offsetInBytes, data.lengthInBytes);

        // Write and flush the bytes written
        await File(path).writeAsBytes(bytes, flush: true);
      }

      // open the database
      return await openDatabase(path, readOnly: true);
    }

    Future<List<Map>> search(String term) async {
      final db = await getDatabase();
      final List<Map> results = await db.rawQuery(
        '''
        SELECT t.term, t.reading, d.definition
        FROM terms t
        INNER JOIN definitions d ON t.id = d.term_id
        WHERE t.term = ?
        ''', [term]);
      return results;
    }
    ```

## Database Schema

The database consists of two tables:

*   `terms`: This table contains the dictionary terms.
    *   `id`: The primary key for the table.
    *   `term`: The Japanese term (e.g., '食べる').
    *   `reading`: The reading of the term (e.g., 'たべる').
    *   `popularity`: A score representing the popularity of the term.
    *   `sequence`: A unique identifier for the entry.

*   `definitions`: This table contains the definitions for the terms.
    *   `id`: The primary key for the table.
    *   `term_id`: A foreign key that references the `id` column in the `terms` table.
    *   `definition`: The English definition of the term.

## Example: Displaying Data in a Flutter App

Here is a more complete example of how to query the database and display the results in a Flutter widget.

First, define a `Term` model class to hold the data from the database:

```dart
class Term {
  final String term;
  final String reading;
  final String definition;

  Term({required this.term, required this.reading, required this.definition});

  @override
  String toString() {
    return 'Term{term: $term, reading: $reading, definition: $definition}';
  }
}
```

Next, create a function to search for a term and map the results to a list of `Term` objects:

```dart
Future<List<Term>> search(String searchTerm) async {
  final db = await getDatabase();
  final List<Map<String, dynamic>> maps = await db.rawQuery(
    '''
    SELECT t.term, t.reading, d.definition
    FROM terms t
    INNER JOIN definitions d ON t.id = d.term_id
    WHERE t.term = ?
    ''', [searchTerm]);

  return List.generate(maps.length, (i) {
    return Term(
      term: maps[i]['term'],
      reading: maps[i]['reading'],
      definition: maps[i]['definition'],
    );
  });
}
```

Finally, you can use this function in a `FutureBuilder` to display the data in a widget:

```dart
class SearchResults extends StatelessWidget {
  final String searchTerm;

  SearchResults({required this.searchTerm});

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Term>>(
      future: search(searchTerm),
      builder: (context, snapshot) {
        if (snapshot.hasData) {
          return ListView.builder(
            itemCount: snapshot.data!.length,
            itemBuilder: (context, index) {
              return ListTile(
                title: Text(snapshot.data![index].term),
                subtitle: Text(snapshot.data![index].reading),
                trailing: Text(snapshot.data![index].definition),
              );
            },
          );
        } else if (snapshot.hasError) {
          return Text("${snapshot.error}");
        }
        return CircularProgressIndicator();
      },
    );
  }
}
```
