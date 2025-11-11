# Estructura de Datos del Diccionario Jitendex

Este documento describe la estructura de datos del diccionario Jitendex y qué información está disponible para mostrar en el frontend.

## Esquema de Base de Datos

La base de datos SQLite contiene **2 tablas relacionadas**:

### Tabla `terms` (Términos)

Contiene las entradas principales del diccionario japonés.

| Campo        | Tipo    | Descripción                                         |
| ------------ | ------- | --------------------------------------------------- |
| `id`         | INTEGER | Primary Key (autoincremental)                       |
| `term`       | TEXT    | Término en japonés (kanji/kana). Ej: `食べる`, `猫` |
| `reading`    | TEXT    | Lectura en hiragana. Ej: `たべる`, `ねこ`           |
| `popularity` | INTEGER | Puntuación de popularidad del término               |
| `sequence`   | INTEGER | Identificador único de la entrada (UNIQUE)          |

### Tabla `definitions` (Definiciones)

Contiene las definiciones en inglés. **Relación 1:N con `terms`** (un término puede tener múltiples definiciones).

| Campo        | Tipo    | Descripción                   |
| ------------ | ------- | ----------------------------- |
| `id`         | INTEGER | Primary Key (autoincremental) |
| `term_id`    | INTEGER | Foreign Key → `terms.id`      |
| `definition` | TEXT    | Definición en inglés          |

---

## ¿Qué mostrar en el Frontend?

### Vista de Búsqueda/Resultado

Cuando un usuario busca un término japonés, puedes mostrar:

```text
📝 食べる
   たべる
   ━━━━━━━━━━━━━━━━━
   • to eat
   • to consume
   • to receive (a blow)

   Popularidad: 4500
```

### Datos Disponibles por Término

1. **Término principal** (`term`)

   - Palabra en japonés (kanji/kana)
   - Usar como título principal

2. **Lectura** (`reading`)

   - Pronunciación en hiragana
   - Mostrar debajo del término o como furigana

3. **Definiciones** (`definition`)

   - Lista de significados en inglés
   - Mostrar como lista con bullets
   - Pueden ser múltiples por término

4. **Popularidad** (`popularity`)
   - Número que indica frecuencia de uso
   - Útil para ordenar resultados
   - Opcional: mostrar con indicador visual (estrellas, barras)

### Query SQL Típico

```sql
SELECT
    t.term,
    t.reading,
    t.popularity,
    d.definition
FROM terms t
INNER JOIN definitions d ON t.id = d.term_id
WHERE t.term = '食べる'
ORDER BY d.id;
```

**Resultado ejemplo:**

```text
term: 食べる
reading: たべる
popularity: 4500
definitions:
  - to eat
  - to consume
  - to receive (a blow)
```

---

## Estructura del Modelo (Frontend/Flutter)

### Modelo de Datos Sugerido

```dart
class DictionaryEntry {
  final String term;        // Término japonés
  final String reading;     // Lectura en hiragana
  final int popularity;     // Puntuación de popularidad
  final List<String> definitions;  // Lista de definiciones

  DictionaryEntry({
    required this.term,
    required this.reading,
    required this.popularity,
    required this.definitions,
  });
}
```

### Ejemplo de Uso en Flutter

```dart
// Buscar término
Future<DictionaryEntry?> searchTerm(String searchTerm) async {
  final db = await database;

  final results = await db.rawQuery('''
    SELECT t.term, t.reading, t.popularity, d.definition
    FROM terms t
    INNER JOIN definitions d ON t.id = d.term_id
    WHERE t.term = ?
  ''', [searchTerm]);

  if (results.isEmpty) return null;

  return DictionaryEntry(
    term: results.first['term'] as String,
    reading: results.first['reading'] as String,
    popularity: results.first['popularity'] as int,
    definitions: results.map((r) => r['definition'] as String).toList(),
  );
}
```

---

## Casos de Uso Comunes

### 1. Búsqueda Exacta

```sql
WHERE t.term = '猫'
```

### 2. Búsqueda por Inicio (Autocompletar)

```sql
WHERE t.term LIKE '食%'
```

### 3. Búsqueda por Lectura

```sql
WHERE t.reading = 'たべる'
```

### 4. Términos Más Populares

```sql
ORDER BY t.popularity DESC
LIMIT 50
```

### 5. Búsqueda en Definiciones

```sql
WHERE d.definition LIKE '%eat%'
```

---

## Notas Importantes

1. **Relación 1:N**: Un término puede tener **múltiples definiciones**. Asegúrate de agruparlas en el frontend.

2. **Lectura**: Siempre en hiragana, útil para mostrar furigana o para buscar por pronunciación.

3. **Popularidad**: Valores más altos = términos más comunes. Úsalo para ordenar resultados de búsqueda.

4. **Base de datos de solo lectura**: Optimizada para consultas, no requiere modificaciones en runtime.

5. **Structured Content**: Las definiciones ya están procesadas y extraídas como texto plano (el parser maneja el formato complejo de Yomitan internamente).

---

## Ejemplo Visual de Tarjeta de Término

```text
┌─────────────────────────────────────┐
│ 食べる                              │ ← term
│ たべる                              │ ← reading
├─────────────────────────────────────┤
│ 📖 Definiciones:                    │
│   • to eat                          │ ← definitions[0]
│   • to consume                      │ ← definitions[1]
│   • to receive (a blow)             │ ← definitions[2]
├─────────────────────────────────────┤
│ ⭐ Popularidad: ████░ (4500)        │ ← popularity
└─────────────────────────────────────┘
```
