# 🎰 Casino UTN

> Juego de casino para la consola, hecho en Python: cuatro juegos, persistencia en archivos binarios, ranking de jugadores y un módulo de administración con ABM. Todo dibujado en la terminal con colores ANSI y animaciones.

**Trabajo Práctico N.º 3 · Algoritmos y Estructuras de Datos** · Ingeniería en Sistemas de Información · UTN

*English summary: a terminal-based casino game written in Python for a university Algorithms & Data Structures course. It features four games, binary-file persistence with `pickle`, a player ranking sorted directly on disk, an admin CRUD module, and a fully custom ANSI-rendered UI with animations.*

<!-- Agregar acá una captura o GIF del juego: docs/demo.gif -->
<!-- ![Casino UTN](docs/demo.gif) -->

---

## Qué hace

Al entrar, un croupier dibujado en pixel art te recibe en el lobby. Cada jugador se identifica con su nombre: si es nuevo, se lo da de alta con **$ 10.000** de crédito inicial, y si ya existe, se recupera su saldo y su historial.

| Mesa | Juego | Cómo se gana |
|---|---|---|
| **A** | **Menor-Mayor** | Elegís una categoría (por ejemplo, *Películas*: ¿cuál se estrenó más tarde?) y en cada una de las 6 rondas elegís la opción de mayor valor. Con 4 aciertos o más ganás lo apostado. |
| **B** | **Número secreto** | Abrís la bóveda adivinando un número del 1 al 100 en 5 intentos, con pistas de *mayor* o *menor*. |
| **C** | **Blackjack** | Llegás a 21 sin pasarte, contra la banca. Mazo mezclado, carta oculta del crupier y animaciones de reparto. |
| **D** | **Par o impar** | Se tiran dos dados y apostás si la suma es par o impar. |
| **E** | **Reporte** | El libro de la casa: ranking de jugadores ordenado por crédito y el detalle de partidas ganadas y perdidas de un jugador. |
| **F** | **Administración** | Módulo protegido con contraseña: alta, modificación y baja de categorías, y alta y consulta de opciones del Menor-Mayor. |

---

## Lo técnico

**Archivos binarios con `pickle`, sin base de datos.** Los datos viven en tres archivos de registros (`categorias.dat`, `opciones.dat` y `jugadores.dat`). El acceso es directo por posición: se guarda el offset de cada registro con `tell()` y se reescribe en el lugar con `seek()`. Los campos de texto tienen largo fijo (con relleno), así todos los registros ocupan lo mismo.

**Ordenamiento sobre el archivo.** El ranking ordena `jugadores.dat` directamente en disco, intercambiando registros por posición (`posición = i × tamaño_de_registro`), sin cargar todo en memoria.

**Bajas lógicas.** Las categorías no se borran: se marcan con un estado (`A` activa, `I` inactiva) y los juegos solo usan las activas.

**Interfaz propia en la consola.** No usa librerías externas. La pantalla se arma como una matriz de celdas (carácter y color) que se vuelca con secuencias de escape ANSI: colores de 256 tonos, posicionamiento de cursor, letras grandes, cartas, dados, fichas, carteles de neón y un croupier que cambia de cara según lo que pasa. La lectura de teclas sin Enter usa `msvcrt`.

**Validación de entradas.** Todos los ingresos se validan (rangos numéricos, opciones de menú, contraseña oculta con máximo 3 intentos).

### Modelo de datos

```text
Categoria   nro_categoria · nombre (30) · pregunta (200) · estado (A/I)
Opcion      nro_categoria · nro_opcion · objeto (100) · valor
Jugador     nombre (30) · creditos · juegos[2][4]   ← ganadas/perdidas por cada juego
```

---

## Cómo ejecutarlo

**Requisitos:** Windows (usa `msvcrt` para leer el teclado) y **Python 3.10 o superior** (usa `match`). No hace falta instalar ninguna librería.

```bash
git clone https://github.com/<tu-usuario>/casino-utn.git
cd casino-utn
python casino_utn.py
```

- Usá una terminal de **al menos 100 × 30** caracteres. Si es más chica, el juego te avisa y espera a que la agrandes.
- Funciona mejor en **Windows Terminal**.
- El repo ya trae cargadas 3 categorías con 30 opciones (*Equipos de fútbol argentino*, *Famosos* y *Películas*). El archivo de jugadores se crea solo la primera vez.
- La contraseña del módulo de administración es `admin123`. Es una clave de ejemplo, fija en el código.

## Estructura

```text
casino-utn/
├── casino_utn.py      # programa completo
├── data/
│   ├── categorias.dat # categorías del Menor-Mayor
│   └── opciones.dat   # opciones de cada categoría
└── docs/              # capturas
```

---

## Equipo

Trabajo hecho en equipo para la cursada:

- **Ignacio Robles**
- Máximo Vitulich
- Valentino Roccia
- Renzo Santi

## Nota

Es un trabajo académico, así que sigue las convenciones de la materia: programación estructurada, archivos binarios en lugar de una base de datos y sin librerías externas.
