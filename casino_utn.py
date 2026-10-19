# Maximo Vitulich
# Ignacio Robles
# Valentino Roccia
# Renzo Santi

import random
import os
import time
import pickle
import msvcrt

class Categoria:
    def __init__(self):
        self.nro_categoria = 0
        self.nombre = " " * 30
        self.pregunta = " " * 200
        self.estado = "A"


class Opcion:
    def __init__(self):
        self.nro_categoria = 0
        self.nro_opcion = 0
        self.objeto = " " * 100
        self.valor = 0


class Jugador:
    def __init__(self):
        self.nombre = " " * 30
        self.creditos = 10000.0
        self.juegos = [[0] * 4 for i in range(2)]

# Los archivos de datos se guardan en la carpeta "data" junto al programa
RUTA_CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data") + os.sep
RUTA_CATEGORIAS = RUTA_CARPETA + "categorias.dat"
RUTA_OPCIONES = RUTA_CARPETA + "opciones.dat"
RUTA_JUGADORES = RUTA_CARPETA + "jugadores.dat"

CLAVE_ADMIN = "admin123"

CREDITO_INICIAL = 10000.0


def crearSiNoExiste(ruta):
    if not os.path.exists(ruta):
        archivo = open(ruta, "wb")
        archivo.close()


def prepararArchivos():
    if not os.path.exists(RUTA_CARPETA):
        os.makedirs(RUTA_CARPETA)
    crearSiNoExiste(RUTA_CATEGORIAS)
    crearSiNoExiste(RUTA_OPCIONES)
    crearSiNoExiste(RUTA_JUGADORES)

prepararArchivos()

def ajustarTexto(texto, largo):
    resultado = texto
    while len(resultado.encode("utf-8")) > largo:
        resultado = resultado[:-1]
    resultado = resultado + " " * (largo - len(resultado.encode("utf-8")))
    return resultado

def buscarJugador(nombre):
    global BU_pos, BU_encontrado

    BU_pos = 0
    BU_encontrado = False
    nombre_ajustado = ajustarTexto(nombre, 30)
    tam = os.path.getsize(RUTA_JUGADORES)

    archivo = open(RUTA_JUGADORES, "rb")
    while archivo.tell() < tam and BU_encontrado == False:
        pos = archivo.tell()
        reg = pickle.load(archivo)
        if reg.nombre == nombre_ajustado:
            BU_encontrado = True
            BU_pos = pos
    archivo.close()


def altaJugador(nombre):
    global BU_pos

    reg = Jugador()
    reg.nombre = ajustarTexto(nombre, 30)
    reg.creditos = 10000.0

    BU_pos = os.path.getsize(RUTA_JUGADORES)
    archivo = open(RUTA_JUGADORES, "ab")
    pickle.dump(reg, archivo)
    archivo.close()

def leerJugador(pos):
    archivo = open(RUTA_JUGADORES, "rb")
    archivo.seek(pos)
    reg = pickle.load(archivo)
    archivo.close()
    return reg


def grabarJugador(pos, reg):
    archivo = open(RUTA_JUGADORES, "r+b")
    archivo.seek(pos)
    pickle.dump(reg, archivo)
    archivo.close()

def registrarResultado(pos, juego, gano, cambio_creditos):
    reg = leerJugador(pos)

    if gano == True:
        fila = GANADAS
    else:
        fila = PERDIDAS

    reg.juegos[fila][juego] = reg.juegos[fila][juego] + 1
    reg.creditos = reg.creditos + cambio_creditos
    grabarJugador(pos, reg)


# Lo llaman los 4 juegos al empezar. Pide el nombre, lo busca en jugadores.dat
# y, si no existe, lo da de alta con el credito inicial. El croupier lo recibe.
# Deja el resultado en JU_nombre (el nombre) y JU_pos (su posicion en el archivo).
#texto, nombre: string - inicio: int - reg: Jugador

def identificarJugador():
    global JU_pos, JU_nombre, ES_nombre

    texto = pedirTexto("Ingrese su nombre: ", 30)

    # se sacan los espacios del principio y del final
    inicio = 0
    while inicio < len(texto) and texto[inicio] == " ":
        inicio = inicio + 1
    nombre = limpiarTexto(texto[inicio:])

    buscarJugador(nombre)
    if BU_encontrado == False:
        altaJugador(nombre)
        decir("Bienvenido, " + nombre + ".", "Fuiste registrado con $ " + formatoMiles(int(CREDITO_INICIAL)) + " de crédito.",
              "", OJ_FRENTE, BO_SONRISA)
    else:
        reg = leerJugador(BU_pos)
        decir("Bienvenido de nuevo, " + nombre + ".", "Tu crédito es: $ " + formatoMiles(int(reg.creditos)),
              "", OJ_FRENTE, BO_SONRISA)

    JU_pos = BU_pos
    JU_nombre = nombre
    ES_nombre = nombre


# Filas de la matriz juegos
GANADAS = 0
PERDIDAS = 1

# Columnas de la matriz juegos
MAYOR_MENOR = 0
NUM_SECRETO = 1
BLACKJACK = 2
PAR_IMPAR = 3



# =============================================================================
# VARIABLES DE SALIDA DE LOS MÓDULOS GENERALES
# =============================================================================
# BU_pos - NU_numero - JU_pos: int
# BU_encontrado: boolean
# OP_elegida - JU_nombre: string

BU_pos = 0
BU_encontrado = False
OP_elegida = ""
NU_numero = 0
JU_pos = 0
JU_nombre = ""


# =============================================================================
# PANTALLA DEL CASINO (la usan todas las opciones del menu)
# =============================================================================
# Todo el programa se dibuja en una "pantalla" propia de 30 x 100 celdas: una
# matriz con el caracter de cada celda y otra con su color (codigo ANSI).
# Cada cuadro se arma ahi y despues se manda entero a la consola de una sola
# vez, asi no parpadea. Arriba esta el croupier, abajo el paño de la mesa.

ANCHO = 100
ALTO = 30
# PA_car: matriz de 30 x 100 string (el caracter de cada celda)
# PA_col: matriz de 30 x 100 string (el codigo de color de cada celda)
PA_car = [[" "] * ANCHO for i in range(ALTO)]
PA_col = [[""] * ANCHO for i in range(ALTO)]

# Lugares fijos de la pantalla
FILA_MESA = 12          # baranda de madera entre el croupier y el paño
FILA_CONTENIDO = 13     # primera fila del paño (listas, menus y juegos)
FILA_ENTRADA = 26       # caja donde el jugador escribe (filas 25 a 27)
FILA_BARRA = 29         # barra de botones y avisos
CR_FILA = 0             # croupier
CR_COL = 4
BUR_COL = 38            # globo de dialogo

# Colores (paleta de 256 colores de la consola)
C_NEGRO = 16
C_BLANCO = 255
C_CREMA = 230
C_GRIS = 250
C_GRIS_OSCURO = 240
C_ORO = 178
C_ORO_CLARO = 220
C_ORO_OSCURO = 136
C_ROJO_CARTA = 160
C_ROJO_VIVO = 196
C_ROJO_AVISO = 203
C_VERDE = 46
C_VERDE_CLARO = 157
C_ROJO_CLARO = 217
C_NARANJA = 208
C_CIAN = 51
C_NEON = 213
C_MADERA = 94
C_MADERA_CLARA = 130
C_DORSO = 88
C_DORSO_DIBUJO = 124
C_RETRATO = 229
C_CAJA = 235
C_BARRA = 234

# Pantallas (cada mesa del casino)
PANT_MENU = 0
PANT_MM = 1
PANT_NS = 2
PANT_BJ = 3
PANT_PI = 4
PANT_REP = 5
PANT_ADMIN = 6

# Color del paño y de su sombra, y del saco y la solapa del croupier en cada mesa
# MESA_PANOS, MESA_SOMBRAS, MESA_SACOS, MESA_SOLAPAS: array de 7 int
MESA_PANOS = [52, 24, 23, 28, 88, 53, 236]
MESA_SOMBRAS = [233, 17, 233, 22, 52, 233, 233]
MESA_SACOS = [52, 18, 23, 52, 22, 94, 240]
MESA_SOLAPAS = [88, 26, 30, 88, 28, 130, 244]

# Mesa actual
# MESA_tipo, MESA_pano, MESA_base, MESA_sombra, ANIM_fase: int
MESA_tipo = PANT_MENU
MESA_pano = 52
MESA_base = 52
MESA_sombra = 233
ANIM_fase = 0

# El croupier esta dibujado con "pixeles": cada letra es un color, y cada celda
# de la consola muestra 2 pixeles (uno arriba y otro abajo) con el caracter ▀.
# . transparente - H pelo - h brillo - S piel - s sombra - K ojos y cejas
# W blanco - J saco - V solapa - R moño - G botones - M boca
CR_ARTE = [
    "..........HHHHHHHH..........",
    ".......HHHHHHHHHHHHHH.......",
    "......HHHHhhhhHHHHHHHH......",
    ".....HHHhhHHHHHHHHHHHHH.....",
    ".....HHHHHHHHHHHHHHHHHH.....",
    ".....HHHSSSSSSSSSSSSHHH.....",
    ".....HHSSSSSSSSSSSSSSHH.....",
    ".....HSSKKKKSSSSKKKKSSH.....",
    "....sSSSSSSSSSSSSSSSSSSs....",
    "....sSSSWKSSSSSSSSKWSSSs....",
    "....sSSSSSSSSssSSSSSSSSs....",
    ".....SSSSSSSSssSSSSSSSS.....",
    ".....SSSSSSSSSSSSSSSSSS.....",
    ".....SSSSSSSMMMMSSSSSSS.....",
    "......sSSSSSSSSSSSSSSs......",
    ".......ssSSSSSSSSSSss.......",
    ".........sssSSSSsss.........",
    "..........WWSSSSWW..........",
    "......JJJJWWRRRRWWJJJJ......",
    "....JJJJJJVWRRRRWVJJJJJJ....",
    "...JJJJJJJVVWWWWVVJJJJJJJ...",
    "..JJJJJJJJVVWGGWVVJJJJJJJJ..",
    "..JJJJJJJJVVVWWVVVJJJJJJJJ..",
    ".JJJJJJJJJVVVGGVVVJJJJJJJJJ.",
]
PIX_LETRAS = "HhSsKWJVRGM"
PIX_COLORES = [235, 240, 223, 180, 234, 255, 52, 88, 16, 178, 131]

# Caras del croupier: los ojos son la fila 9 del dibujo y la boca las filas 13 y 14
OJ_FRENTE = 0
OJ_IZQ = 1
OJ_DER = 2
OJ_CERRADOS = 3
OJ_GUINO = 4
CR_OJO_IZQ = ["WK", "KW", "WK", "KK", "WK"]
CR_OJO_DER = ["KW", "KW", "WK", "KK", "KK"]

BO_NEUTRAL = 0
BO_SONRISA = 1
BO_SORPRESA = 2
BO_PICARO = 3
BO_SERIO = 4
BO_HABLANDO = 5
CR_BOCA_A = ["SMMMMS", "MSSSSM", "SSMMSS", "MWWWWM", "SSSSSS", "SMMMMS"]
CR_BOCA_B = ["SSSSSS", "SMMMMS", "SSMMSS", "SMMMMS", "SMMMMS", "SSMMSS"]

# Estado de lo que se ve en pantalla
# CR_ojos, CR_boca, ES_banner_fg, ES_banner_bg, ES_banner_fila: int
# ES_texto: array de 3 string (las lineas del globo)
# ES_placa, ES_info, ES_nombre, ES_barra, ES_aviso, ES_banner, ES_pregunta: string
# ES_tecla1, ES_boton1, ES_tecla2, ES_boton2: string - ES_pulso: boolean
CR_ojos = OJ_FRENTE
CR_boca = BO_NEUTRAL
ES_banner_fg = C_NEGRO
ES_banner_bg = C_ORO
ES_banner_fila = 23
ES_texto = ["", "", ""]
ES_placa = ""
ES_info = ""
ES_nombre = ""
ES_barra = ""
ES_aviso = ""
ES_banner = ""
ES_pregunta = ""
ES_tecla1 = ""
ES_boton1 = ""
ES_tecla2 = ""
ES_boton2 = ""
ES_pulso = False

# Lista que se muestra en el paño (categorias, opciones...). Entran 22 por
# pagina en dos columnas; si hay mas, se pasa de pagina con ENTER.
# CO_titulo: string - CO_items: array de 22 string - CO_cant: int
CO_MAX = 22
CO_titulo = ""
CO_items = [""] * CO_MAX
CO_cant = 0

# Menu de fichas que se muestra en el paño
# MN_titulo: string - MN_teclas, MN_textos, MN_descrs: array de 8 string
# MN_colores: array de 8 int - MN_cant, MN_sel: int
MN_titulo = ""
MN_teclas = [""] * 8
MN_textos = [""] * 8
MN_descrs = [""] * 8
MN_colores = [0] * 8
MN_cant = 0
MN_sel = -1

# Texto partido en renglones (lo deja partirTexto)
# WR_lineas: array de 3 string - WR_cant: int
WR_lineas = ["", "", ""]
WR_cant = 0

# Variable de salida de esperarTecla
# TE_tecla: string
TE_tecla = ""

# Letras grandes (5 x 5) para carteles y numeros: # = lleno
# FUENTE_LETRAS: string - FUENTE: array de string (5 renglones por letra)
FUENTE_LETRAS = "0123456789CASINOUT?"
FUENTE = [
    " ### ", "#   #", "#   #", "#   #", " ### ",
    "  #  ", " ##  ", "  #  ", "  #  ", " ### ",
    " ### ", "#   #", "  ## ", " #   ", "#####",
    "#### ", "    #", " ### ", "    #", "#### ",
    "#   #", "#   #", "#####", "    #", "    #",
    "#####", "#    ", "#### ", "    #", "#### ",
    " ### ", "#    ", "#### ", "#   #", " ### ",
    "#####", "    #", "   # ", "  #  ", "  #  ",
    " ### ", "#   #", " ### ", "#   #", " ### ",
    " ### ", "#   #", " ####", "    #", " ### ",
    " ####", "#    ", "#    ", "#    ", " ####",
    " ### ", "#   #", "#####", "#   #", "#   #",
    " ####", "#    ", " ### ", "    #", "#### ",
    "#####", "  #  ", "  #  ", "  #  ", "#####",
    "#   #", "##  #", "# # #", "#  ##", "#   #",
    " ### ", "#   #", "#   #", "#   #", " ### ",
    "#   #", "#   #", "#   #", "#   #", " ### ",
    "#####", "  #  ", "  #  ", "  #  ", "  #  ",
    " ### ", "#   #", "  ## ", "     ", "  #  ",
]


# =============================================================================
# VARIABLES GLOBALES - JUEGO A: MENOR-MAYOR (MM)
# =============================================================================
# MM_ronda, MM_apuesta, MM_val_izq, MM_val_der, MM_vis_izq, MM_vis_der: int
# MM_elegida, MM_ganador, MM_desp: int - MM_resultados: array de 6 int (0 sin jugar, 1 bien, 2 mal)
# MM_izq, MM_der, MM_pregunta: string - MM_revelado, MM_resaltar, MM_acerto: boolean
MM_ronda = 0
MM_apuesta = 0
MM_val_izq = 0
MM_val_der = 0
MM_vis_izq = 0
MM_vis_der = 0
MM_elegida = 0
MM_ganador = 0
MM_desp = 0
MM_resultados = [0] * 6
MM_izq = ""
MM_der = ""
MM_pregunta = ""
MM_revelado = False
MM_resaltar = False
MM_acerto = False


# =============================================================================
# VARIABLES GLOBALES - JUEGO B: NUMERO SECRETO (NS)
# =============================================================================
# NS_min, NS_max, NS_ultimo, NS_pista, NS_restantes: int
# NS_display: string - NS_activo, NS_revelado, NS_adivino: boolean
NS_min = 1
NS_max = 100
NS_ultimo = 0
NS_pista = 0
NS_restantes = 5
NS_display = "???"
NS_activo = False
NS_revelado = False
NS_adivino = False


# =============================================================================
# VARIABLES GLOBALES - JUEGO C: BLACKJACK (BJ)
# =============================================================================
TAM_MANO = 15

# BJ_mazo: array de 53 boolean. Se usan los indices 1 al 52, uno por carta.
#          True = la carta ya salio en esta partida (no se puede repetir).
BJ_mazo = [False] * 53

# Datos de la ultima carta repartida (los deja repartirCartaBJ)
# BJ_id_carta, BJ_valor_carta, BJ_usadas: int - BJ_es_as: boolean
BJ_id_carta = 0
BJ_valor_carta = 0
BJ_es_as = False
BJ_usadas = 0

# Tablas de la baraja: en vez de preguntar con if por cada palo y cada figura,
# se busca el dato directo por el numero de palo (0 a 3) o de figura (1 a 13).
BJ_SIMBOLOS = ["♠", "♥", "♦", "♣"]
BJ_FIGURAS = ["", "A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
BJ_VALORES = [0, 11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

# Donde va cada pinta en las cartas del As al 10, como en una baraja real.
# Son pares de digitos (fila, columna) dentro de la carta: "1454" = (1,4) y (5,4)
BJ_PINTAS = ["", "34", "1454", "143454", "12165256", "1216525634",
             "121632365256", "12163236525624", "1216323652562444",
             "121622264246525634", "12162226424652562444"]

# Manos de la partida. JUGADOR y BANCA son la fila de cada uno en las matrices.
JUGADOR = 0
BANCA = 1

# BJ_ids: matriz de 2 x 15 int (el id, de 1 a 52, de cada carta de cada mano)
# BJ_cant_cartas - BJ_totales - BJ_ases: array de 2 int
BJ_ids = [[0] * TAM_MANO for i in range(2)]
BJ_cant_cartas = [0, 0]
BJ_totales = [0, 0]
BJ_ases = [0, 0]

# Lugares de la mesa de Blackjack
FILA_LEYENDA = 21
ZA_FILA = 15            # zapato, de donde salen las cartas
ZA_COL = 90

# ES_omitir_quien, ES_omitir_indice, PC_fila, PC_col: int - ES_oculta: boolean
ES_omitir_quien = -1
ES_omitir_indice = -1
ES_oculta = True
PC_fila = 0
PC_col = 0

# Frases del croupier cuando el jugador pide carta (se elige una al azar)
FR_PEDIR = ["Interesante...", "Se pone picante la cosa.", "Mmm... arriesgado.",
            "Veamos qué te depara el mazo.", "La suerte está echada."]


# =============================================================================
# VARIABLES GLOBALES - JUEGO D: PAR O IMPAR (PI)
# =============================================================================
# Donde van los puntos de cada cara del dado: pares (fila, columna) de 0 a 2
# PI_PUNTOS: array de 7 string
PI_PUNTOS = ["", "11", "0022", "001122", "00022022", "0002112022", "000210122022"]
# PI_dado1, PI_dado2, PI_salto1, PI_salto2, PI_corr1, PI_corr2, PI_apuesta, PI_suma: int
# PI_eleccion, PI_resultado: string
PI_dado1 = 0
PI_dado2 = 0
PI_salto1 = 0
PI_salto2 = 0
PI_corr1 = 0
PI_corr2 = 0
PI_apuesta = 0
PI_suma = 0
PI_eleccion = ""
PI_resultado = ""


# =============================================================================
# VARIABLES GLOBALES - OPCION E: REPORTE (REP)
# =============================================================================
# REP_modo: int (0 nada, 1 ranking, 2 ficha de un jugador)
# REP_pos: array de 11 int - REP_nom: array de 11 string - REP_cred: array de 11 float
# REP_cant, REP_maximo, REP_jcant: int - REP_nombre: string - REP_creditos: float
# REP_jnom: array de 4 string - REP_jg, REP_jp: array de 4 int
REP_modo = 0
REP_pos = [0] * 11
REP_nom = [""] * 11
REP_cred = [0.0] * 11
REP_cant = 0
REP_maximo = 0
REP_nombre = ""
REP_creditos = 0.0
REP_jnom = [""] * 4
REP_jg = [0] * 4
REP_jp = [0] * 4
REP_jcant = 0


# =============================================================================
# MÓDULOS DE LA PANTALLA DEL CASINO
# =============================================================================

#fg, bg: int

def colorANSI(fg, bg):
    return "\033[38;5;" + str(fg) + ";48;5;" + str(bg) + "m"


#fila, col: int - car, color: string

def ponerCelda(fila, col, car, color):
    if fila >= 0 and fila < ALTO and col >= 0 and col < ANCHO:
        PA_car[fila][col] = car
        PA_col[fila][col] = color


#fila, col, i: int - texto, color: string

def pegarTexto(fila, col, texto, color):
    for i in range(len(texto)):
        ponerCelda(fila, col + i, texto[i], color)


#fila: int - texto, color: string

def pegarCentrado(fila, texto, color):
    pegarTexto(fila, (ANCHO - len(texto)) // 2, texto, color)


# Manda a la consola las filas desde..hasta, todas juntas en un solo print.
# Solo cambia de color cuando la celda tiene un color distinto a la anterior.
#desde, hasta, f, c, limite: int - salida, actual: string

def volcarFilas(desde, hasta):
    salida = ""
    for f in range(desde, hasta + 1):
        salida = salida + "\033[" + str(f + 1) + ";1H"
        actual = ""
        limite = ANCHO
        if f == ALTO - 1:
            limite = ANCHO - 1      # la ultima celda no se escribe, asi la consola no se desplaza
        for c in range(limite):
            if PA_col[f][c] != actual:
                actual = PA_col[f][c]
                salida = salida + actual
            salida = salida + PA_car[f][c]
    print(salida + "\033[0m", end="", flush=True)


def volcarTodo():
    volcarFilas(0, ALTO - 1)


#fila, fondo: int

def fondoFila(fila):
    if fila < FILA_MESA:
        fondo = 232 + fila // 3     # penumbra que se aclara hacia la mesa
    elif fila == FILA_MESA:
        fondo = C_MADERA
    elif fila == FILA_BARRA:
        fondo = C_BARRA
    else:
        fondo = MESA_pano
    return fondo


#f, c, fondo: int

def dibujarFondo():
    for f in range(ALTO):
        fondo = fondoFila(f)
        for c in range(ANCHO):
            if f == FILA_MESA - 1:
                ponerCelda(f, c, "▄", colorANSI(C_MADERA_CLARA, fondo))
            elif f == FILA_MESA + 1 and c >= 2 and c < ANCHO - 2:
                # media fila de sombra de la baranda sobre el paño
                ponerCelda(f, c, "▀", colorANSI(MESA_sombra, fondo))
            elif f > FILA_MESA and f < FILA_BARRA and (c < 2 or c >= ANCHO - 2):
                ponerCelda(f, c, " ", colorANSI(C_GRIS, MESA_sombra))
            else:
                ponerCelda(f, c, " ", colorANSI(C_GRIS, fondo))


# Texto con separador de miles: 1234567 -> "1.234.567"
#numero, i, cont: int - texto, resultado: string

def formatoMiles(numero):
    texto = str(numero)
    resultado = ""
    cont = 0
    for i in range(len(texto) - 1, -1, -1):
        resultado = texto[i] + resultado
        cont = cont + 1
        if cont % 3 == 0 and i > 0 and texto[i - 1] != "-":
            resultado = "." + resultado
    return resultado


# Parte un texto en hasta 3 renglones de "ancho" letras sin cortar palabras.
# Deja los renglones en WR_lineas y la cantidad en WR_cant.
#texto, linea, palabra, candidata: string - ancho, i: int

def partirTexto(texto, ancho):
    global WR_lineas, WR_cant
    WR_lineas = ["", "", ""]
    WR_cant = 0
    linea = ""
    palabra = ""
    for i in range(len(texto) + 1):
        if i == len(texto) or texto[i] == " ":
            if palabra != "":
                if linea == "":
                    candidata = palabra
                else:
                    candidata = linea + " " + palabra
                if len(candidata) <= ancho:
                    linea = candidata
                else:
                    guardarRenglon(linea)
                    linea = palabra[:ancho]
                palabra = ""
        else:
            palabra = palabra + texto[i]
    guardarRenglon(linea)


#linea: string

def guardarRenglon(linea):
    global WR_cant
    if linea != "" and WR_cant < 3:
        WR_lineas[WR_cant] = linea
        WR_cant = WR_cant + 1


#letra: string - i, indice: int

def indiceFuente(letra):
    indice = -1
    i = 0
    while i < len(FUENTE_LETRAS) and indice == -1:
        if FUENTE_LETRAS[i] == letra:
            indice = i
        i = i + 1
    return indice


# Escribe con letras grandes de 5 filas. Con doble = True cada punto ocupa 2 columnas.
#fila, col, x, i, k, r, c, paso: int - texto, color, patron: string - doble: boolean

def pegarGrande(fila, col, texto, color, doble):
    x = col
    paso = 6
    if doble == True:
        paso = 12
    for i in range(len(texto)):
        k = indiceFuente(texto[i])
        if k >= 0:
            for r in range(5):
                patron = FUENTE[k * 5 + r]
                for c in range(5):
                    if patron[c] == "#":
                        if doble == True:
                            ponerCelda(fila + r, x + 2 * c, "█", color)
                            ponerCelda(fila + r, x + 2 * c + 1, "█", color)
                        else:
                            ponerCelda(fila + r, x + c, "█", color)
        x = x + paso


#texto: string - doble: boolean - ancho: int

def anchoGrande(texto, doble):
    ancho = len(texto) * 6 - 1
    if doble == True:
        ancho = len(texto) * 12 - 2
    return ancho


# -----------------------------------------------------------------------------
# Croupier y globo de dialogo
# -----------------------------------------------------------------------------

#ojos, boca: int

def ponerCara(ojos, boca):
    global CR_ojos, CR_boca
    CR_ojos = ojos
    CR_boca = boca


# Devuelve la fila r del dibujo con los ojos y la boca de la cara actual
#r: int - texto: string

def filaCrupier(r):
    texto = CR_ARTE[r]
    if r == 9:
        texto = texto[:8] + CR_OJO_IZQ[CR_ojos] + texto[10:18] + CR_OJO_DER[CR_ojos] + texto[20:]
    elif r == 13:
        texto = texto[:11] + CR_BOCA_A[CR_boca] + texto[17:]
    elif r == 14:
        texto = texto[:11] + CR_BOCA_B[CR_boca] + texto[17:]
    return texto


#letra: string - i, color: int

def colorPixel(letra):
    color = -1
    i = 0
    while i < len(PIX_LETRAS) and color == -1:
        if PIX_LETRAS[i] == letra:
            color = PIX_COLORES[i]
        i = i + 1
    return color


#f, c, fila, fondo, c_arr, c_aba: int - arriba, abajo: string

def dibujarCrupier():
    for f in range(12):
        arriba = filaCrupier(2 * f)
        abajo = filaCrupier(2 * f + 1)
        fila = CR_FILA + f
        fondo = fondoFila(fila)
        for c in range(28):
            c_arr = colorPixel(arriba[c])
            c_aba = colorPixel(abajo[c])
            if fila == FILA_MESA - 1:
                # la baranda de la mesa queda por delante del croupier
                if c_arr != -1:
                    ponerCelda(fila, CR_COL + c, "▄", colorANSI(C_MADERA_CLARA, c_arr))
            elif c_arr != -1 and c_aba != -1:
                ponerCelda(fila, CR_COL + c, "▀", colorANSI(c_arr, c_aba))
            elif c_arr != -1:
                ponerCelda(fila, CR_COL + c, "▀", colorANSI(c_arr, fondo))
            elif c_aba != -1:
                ponerCelda(fila, CR_COL + c, "▄", colorANSI(c_aba, fondo))


#c, f, i: int - globo: string

def dibujarBurbuja():
    globo = colorANSI(C_NEGRO, C_CREMA)
    for c in range(BUR_COL, ANCHO - 2):
        ponerCelda(1, c, "▄", colorANSI(C_CREMA, fondoFila(1)))
        for f in range(2, 7):
            ponerCelda(f, c, " ", globo)
        ponerCelda(7, c, "▀", colorANSI(C_CREMA, fondoFila(7)))
    ponerCelda(6, BUR_COL - 1, "◄", colorANSI(C_CREMA, fondoFila(6)))
    for i in range(3):
        pegarTexto(3 + i, BUR_COL + 3, ES_texto[i], globo)


def dibujarPlaca():
    pegarTexto(9, BUR_COL, ES_placa, colorANSI(C_ORO, fondoFila(9)))
    pegarTexto(10, BUR_COL, ES_info[:60], colorANSI(C_GRIS, fondoFila(10)))


# -----------------------------------------------------------------------------
# Elementos del paño: listas, menus, cartel, caja de entrada y barra
# -----------------------------------------------------------------------------

#i, fila, col: int

def dibujarLista():
    if CO_titulo != "":
        pegarTexto(FILA_CONTENIDO, 6, CO_titulo[:88], colorANSI(C_ORO_CLARO, MESA_pano))
        for i in range(CO_cant):
            if i < 11:
                fila = FILA_CONTENIDO + 1 + i
                col = 6
            else:
                fila = FILA_CONTENIDO + 1 + i - 11
                col = 52
            pegarTexto(fila, col, "♦", colorANSI(C_ORO, MESA_pano))
            pegarTexto(fila, col + 2, CO_items[i][:42], colorANSI(C_BLANCO, MESA_pano))


# Lamparitas que corren alrededor de los carteles
#fila, col, fase, color: int

def bombita(fila, col, fase, fondo):
    if fase < 0:
        color = 238
    elif (fila + col // 2 + fase) % 4 == 0:
        color = 226
    else:
        color = C_ORO_OSCURO
    ponerCelda(fila, col, "●", colorANSI(color, fondo))


#i, c, fila, fondo, tinta, descr: int

def dibujarMenuFichas():
    if MESA_tipo == PANT_MENU:
        for c in range(3, ANCHO - 3, 2):
            bombita(FILA_CONTENIDO, c, ANIM_fase, MESA_pano)
            bombita(FILA_BARRA - 1, c, ANIM_fase, MESA_pano)
    if MN_cant > 0:
        if MN_titulo != "":
            pegarTexto(FILA_CONTENIDO, 6, MN_titulo, colorANSI(C_ORO_CLARO, MESA_pano))
        for i in range(MN_cant):
            fila = FILA_CONTENIDO + 1 + i * 2
            fondo = MESA_pano
            tinta = C_BLANCO
            descr = C_GRIS
            if MN_sel == i:
                fondo = C_ORO_CLARO
                tinta = C_NEGRO
                descr = C_NEGRO
                for c in range(18, 92):
                    ponerCelda(fila, c, " ", colorANSI(tinta, fondo))
            # la ficha: un circulo de color con la tecla adentro
            ponerCelda(fila, 20, "▐", colorANSI(MN_colores[i], fondo))
            pegarTexto(fila, 21, " " + MN_teclas[i] + " ", colorANSI(C_BLANCO, MN_colores[i]))
            ponerCelda(fila, 24, "▌", colorANSI(MN_colores[i], fondo))
            pegarTexto(fila, 28, MN_textos[i], colorANSI(tinta, fondo))
            pegarTexto(fila, 60, MN_descrs[i], colorANSI(descr, fondo))


#c: int

def dibujarBanner():
    if ES_banner != "":
        for c in range(2, ANCHO - 2):
            ponerCelda(ES_banner_fila, c, " ", colorANSI(ES_banner_fg, ES_banner_bg))
        pegarCentrado(ES_banner_fila, ES_banner, colorANSI(ES_banner_fg, ES_banner_bg))


#c: int

def dibujarEntrada():
    if ES_pregunta != "":
        for c in range(4, ANCHO - 4):
            ponerCelda(FILA_ENTRADA - 1, c, "▄", colorANSI(C_CAJA, MESA_pano))
            ponerCelda(FILA_ENTRADA, c, " ", colorANSI(C_BLANCO, C_CAJA))
            ponerCelda(FILA_ENTRADA + 1, c, "▀", colorANSI(C_CAJA, MESA_pano))
        pegarTexto(FILA_ENTRADA, 6, ES_pregunta, colorANSI(C_ORO_CLARO, C_CAJA))


#c, col, fondo: int - b1, b2: string

def dibujarBarra():
    for c in range(ANCHO):
        ponerCelda(FILA_BARRA, c, " ", colorANSI(C_GRIS, C_BARRA))
    if ES_boton1 != "":
        if ES_pulso == True:
            fondo = C_ORO_CLARO
        else:
            fondo = C_ORO
        b1 = "  [" + ES_tecla1 + "]  " + ES_boton1 + "  "
        if ES_boton2 != "":
            b2 = "  [" + ES_tecla2 + "]  " + ES_boton2 + "  "
            col = (ANCHO - len(b1) - 6 - len(b2)) // 2
            pegarTexto(FILA_BARRA, col + len(b1) + 6, b2, colorANSI(C_NEGRO, fondo))
        else:
            col = (ANCHO - len(b1)) // 2
        pegarTexto(FILA_BARRA, col, b1, colorANSI(C_NEGRO, fondo))
        if ES_aviso != "":
            pegarTexto(FILA_BARRA, 2, ES_aviso[:24], colorANSI(C_ROJO_AVISO, C_BARRA))
    elif ES_aviso != "":
        pegarCentrado(FILA_BARRA, ES_aviso, colorANSI(C_ROJO_AVISO, C_BARRA))
    else:
        pegarCentrado(FILA_BARRA, ES_barra, colorANSI(C_GRIS, C_BARRA))


def dibujarEscena():
    dibujarFondo()
    dibujarCrupier()
    dibujarBurbuja()
    dibujarPlaca()
    if MESA_tipo == PANT_BJ:
        dibujarZapato()
        dibujarFichas()
        dibujarLeyenda()
        dibujarManos()
        dibujarTotales()
    elif MESA_tipo == PANT_MM:
        dibujarMM()
    elif MESA_tipo == PANT_NS:
        dibujarNS()
    elif MESA_tipo == PANT_PI:
        dibujarPI()
    elif MESA_tipo == PANT_REP:
        dibujarReporte()
    dibujarMenuFichas()
    dibujarLista()
    dibujarBanner()
    dibujarEntrada()
    dibujarBarra()


# -----------------------------------------------------------------------------
# Teclado, entradas y dialogo
# -----------------------------------------------------------------------------

def descartarTeclas():
    while msvcrt.kbhit() == True:
        msvcrt.getwch()


#letra: string

def aMayuscula(letra):
    if letra >= "a" and letra <= "z":
        letra = chr(ord(letra) - 32)
    return letra


#ojos_antes: int

def parpadear():
    ojos_antes = CR_ojos
    ponerCara(OJ_CERRADOS, CR_boca)
    dibujarCrupier()
    volcarFilas(CR_FILA + 4, CR_FILA + 4)
    time.sleep(0.12)
    ponerCara(ojos_antes, CR_boca)
    dibujarCrupier()
    volcarFilas(CR_FILA + 4, CR_FILA + 4)


# Lo que se mueve mientras el casino espera una tecla: los botones laten,
# el croupier parpadea y las lamparitas del lobby corren.
#ticks: int

def animarEspera(ticks):
    global ES_pulso, ANIM_fase
    if ticks % 10 == 0:
        if ES_pulso == True:
            ES_pulso = False
        else:
            ES_pulso = True
        dibujarBarra()
        volcarFilas(FILA_BARRA, FILA_BARRA)
    if MESA_tipo == PANT_MENU and ticks % 3 == 0:
        ANIM_fase = ANIM_fase + 1
        dibujarMenuFichas()
        volcarFilas(FILA_CONTENIDO, FILA_CONTENIDO)
        volcarFilas(FILA_BARRA - 1, FILA_BARRA - 1)
    if ticks % 70 == 0:
        parpadear()


# Espera que se apriete una tecla y la devuelve en mayuscula.
# Las flechas y teclas de funcion (que mandan 2 codigos) devuelven "".
#tecla: string - leida: boolean - ticks: int

def leerTecla():
    descartarTeclas()
    tecla = ""
    leida = False
    ticks = 0
    while leida == False:
        if msvcrt.kbhit() == True:
            tecla = msvcrt.getwch()
            if tecla == "\x00" or tecla == "\xe0":
                msvcrt.getwch()
                tecla = ""
            else:
                tecla = aMayuscula(tecla)
            leida = True
        else:
            time.sleep(0.05)
            ticks = ticks + 1
            animarEspera(ticks)
    return tecla


# Espera una tecla valida (op1 u op2) y la deja en TE_tecla
#op1, op2, tecla: string

def esperarTecla(op1, op2):
    global TE_tecla, ES_aviso
    TE_tecla = ""
    while TE_tecla == "":
        tecla = leerTecla()
        if tecla == op1 or tecla == op2:
            TE_tecla = tecla
            ES_aviso = ""
        elif op1 == "\r":
            ES_aviso = "Presioná ENTER"
        else:
            ES_aviso = "Usá " + op1 + " o " + op2
        dibujarBarra()
        volcarFilas(FILA_BARRA, FILA_BARRA)


#tecla1, boton1, tecla2, boton2: string

def mostrarBotones(tecla1, boton1, tecla2, boton2):
    global ES_tecla1, ES_boton1, ES_tecla2, ES_boton2
    ES_tecla1 = tecla1
    ES_boton1 = boton1
    ES_tecla2 = tecla2
    ES_boton2 = boton2
    dibujarBarra()
    volcarFilas(FILA_BARRA, FILA_BARRA)


# Un solo boton de ENTER para seguir
#texto: string

def esperarEnter(texto):
    mostrarBotones("ENTER", texto, "", "")
    esperarTecla("\r", "\r")
    mostrarBotones("", "", "", "")


#texto: string

def avisar(texto):
    global ES_aviso
    ES_aviso = texto
    ponerCara(CR_ojos, BO_SERIO)
    dibujarCrupier()
    dibujarBarra()
    volcarFilas(0, FILA_MESA)
    volcarFilas(FILA_BARRA, FILA_BARRA)


def limpiarAviso():
    global ES_aviso
    ES_aviso = ""
    dibujarBarra()
    volcarFilas(FILA_BARRA, FILA_BARRA)


# Muestra la caja de entrada sobre el paño con el mensaje y lee lo que se escribe.
#mensaje, texto: string - col: int

def pedirEnMesa(mensaje):
    global ES_pregunta
    ES_pregunta = mensaje
    dibujarEscena()
    volcarTodo()
    col = 7 + len(mensaje)
    print("\033[" + str(FILA_ENTRADA + 1) + ";" + str(col + 1) + "H" + colorANSI(C_BLANCO, C_CAJA) + "\033[?25h",
          end="", flush=True)
    texto = input()
    print("\033[?25l\033[0m", end="", flush=True)
    ES_pregunta = ""
    return texto


# El croupier habla: el texto aparece letra por letra y la boca se mueve.
# Si el jugador aprieta una tecla, el resto del texto aparece de golpe.
#linea1, linea2, linea3, color, letra: string - ojos, boca, i, j, fila, col: int
#lineas: array de 3 string - saltear: boolean

def decir(linea1, linea2, linea3, ojos, boca):
    global ES_texto
    lineas = [linea1[:55], linea2[:55], linea3[:55]]
    ES_texto = ["", "", ""]
    ponerCara(ojos, BO_NEUTRAL)
    dibujarEscena()
    volcarFilas(0, FILA_MESA)
    color = colorANSI(C_NEGRO, C_CREMA)
    saltear = False
    descartarTeclas()

    for i in range(3):
        for j in range(len(lineas[i])):
            letra = lineas[i][j]
            ES_texto[i] = ES_texto[i] + letra
            fila = 3 + i
            col = BUR_COL + 3 + j
            ponerCelda(fila, col, letra, color)
            print("\033[" + str(fila + 1) + ";" + str(col + 1) + "H" + color + letra + "\033[0m", end="", flush=True)
            if saltear == False:
                if j % 3 == 0:
                    if CR_boca == BO_HABLANDO:
                        ponerCara(ojos, BO_NEUTRAL)
                    else:
                        ponerCara(ojos, BO_HABLANDO)
                    dibujarCrupier()
                    volcarFilas(CR_FILA + 6, CR_FILA + 7)
                if letra == "." or letra == "," or letra == "?" or letra == "!":
                    time.sleep(0.09)
                else:
                    time.sleep(0.024)
                if msvcrt.kbhit() == True:
                    descartarTeclas()
                    saltear = True

    ponerCara(ojos, boca)
    dibujarCrupier()
    volcarFilas(0, FILA_MESA)


# Igual que decir, pero parte solo el texto en renglones
#texto: string - ojos, boca: int

def hablar(texto, ojos, boca):
    partirTexto(texto, 55)
    decir(WR_lineas[0], WR_lineas[1], WR_lineas[2], ojos, boca)


# Puntos suspensivos en la barra, para generar suspenso
#texto: string - i: int

def suspenso(texto):
    global ES_barra
    for i in range(4):
        ES_barra = texto + " ." * i
        dibujarBarra()
        volcarFilas(FILA_BARRA, FILA_BARRA)
        time.sleep(0.4)
    ES_barra = ""
    dibujarBarra()
    volcarFilas(FILA_BARRA, FILA_BARRA)


# Listas en el paño
#titulo: string

def empezarLista(titulo):
    global CO_titulo, CO_cant
    CO_titulo = titulo
    CO_cant = 0


# Agrega un renglon a la lista. Si la pagina se llena, la muestra y espera ENTER.
#texto: string

def agregarALista(texto):
    global CO_cant
    if CO_cant == CO_MAX:
        mostrarEnMesa()
        esperarEnter("VER MÁS")
        CO_cant = 0
    CO_items[CO_cant] = texto
    CO_cant = CO_cant + 1


def mostrarEnMesa():
    dibujarEscena()
    volcarTodo()


def cerrarLista():
    global CO_titulo, CO_cant
    CO_titulo = ""
    CO_cant = 0


# Menus de fichas
#titulo: string

def ponerMenu(titulo):
    global MN_titulo, MN_cant, MN_sel
    cerrarLista()
    MN_titulo = titulo
    MN_cant = 0
    MN_sel = -1


#tecla, texto, descr: string - color: int

def agregarOpcionMenu(tecla, texto, descr, color):
    global MN_cant
    MN_teclas[MN_cant] = tecla
    MN_textos[MN_cant] = texto
    MN_descrs[MN_cant] = descr
    MN_colores[MN_cant] = color
    MN_cant = MN_cant + 1


def quitarMenu():
    global MN_cant, MN_sel
    MN_cant = 0
    MN_sel = -1


# La opcion elegida titila antes de entrar
#tecla: string - i, k: int

def elegirOpcionMenu(tecla):
    global MN_sel
    for i in range(MN_cant):
        if MN_teclas[i] == tecla:
            for k in range(6):
                if k % 2 == 0:
                    MN_sel = i
                else:
                    MN_sel = -1
                dibujarEscena()
                volcarFilas(FILA_CONTENIDO, FILA_BARRA)
                time.sleep(0.07)
            MN_sel = i
    dibujarEscena()
    volcarFilas(FILA_CONTENIDO, FILA_BARRA)
    time.sleep(0.15)


# El paño y el cartel del resultado titilan. El cartel queda en ES_banner_fila.
#texto: string - fg, bg, pano_flash, i: int

def celebrar(texto, fg, bg, pano_flash):
    global ES_banner, ES_banner_fg, ES_banner_bg, MESA_pano
    ES_banner = texto
    for i in range(8):
        if i % 2 == 0:
            MESA_pano = pano_flash
            ES_banner_fg = bg
            ES_banner_bg = fg
        else:
            MESA_pano = MESA_base
            ES_banner_fg = fg
            ES_banner_bg = bg
        dibujarEscena()
        volcarFilas(FILA_MESA + 1, FILA_BARRA - 1)
        time.sleep(0.13)
    MESA_pano = MESA_base
    ES_banner_fg = fg
    ES_banner_bg = bg
    dibujarEscena()
    volcarTodo()


def quitarCartel():
    global ES_banner
    ES_banner = ""


#gano: boolean - texto: string

def celebrarResultado(gano, texto):
    if gano == True:
        celebrar(texto, C_NEGRO, C_ORO_CLARO, 34)
    else:
        celebrar(texto, C_BLANCO, C_DORSO, 52)


#texto: string

def ponerInfo(texto):
    global ES_info
    ES_info = texto
    dibujarPlaca()
    volcarFilas(9, 10)


#nombre: string - creditos: int

def infoCredito(nombre, creditos):
    return "Jugador: " + nombre[:14] + "   ·   Crédito: $ " + formatoMiles(creditos)


# El credito de la placa sube o baja de a poco hasta el valor nuevo
#nombre: string - antes, despues, k: int

def animarCredito(nombre, antes, despues):
    for k in range(1, 21):
        ponerInfo(infoCredito(nombre, antes + (despues - antes) * k // 20))
        time.sleep(0.03)


# Se apaga la pantalla de arriba hacia abajo
#f: int

def transicion():
    for f in range(ALTO):
        print("\033[" + str(f + 1) + ";1H\033[48;5;16m\033[2K", end="", flush=True)
        time.sleep(0.006)
    print("\033[0m", end="", flush=True)


# Abre una mesa del casino: cambia el paño y el uniforme del croupier y
# enciende las luces de arriba hacia abajo.
#tipo, f: int - placa: string

def abrirMesa(tipo, placa):
    global MESA_tipo, MESA_pano, MESA_base, MESA_sombra, ES_placa, ES_info, ES_texto
    global ES_barra, ES_aviso, ES_banner, ES_pregunta, ES_banner_fila
    MESA_tipo = tipo
    MESA_base = MESA_PANOS[tipo]
    MESA_pano = MESA_base
    MESA_sombra = MESA_SOMBRAS[tipo]
    PIX_COLORES[6] = MESA_SACOS[tipo]
    PIX_COLORES[7] = MESA_SOLAPAS[tipo]
    ES_placa = placa
    ES_info = ""
    ES_texto = ["", "", ""]
    ES_barra = ""
    ES_aviso = ""
    ES_banner = ""
    ES_pregunta = ""
    ES_banner_fila = 23
    mostrarBotones("", "", "", "")
    cerrarLista()
    quitarMenu()
    ponerCara(OJ_CERRADOS, BO_NEUTRAL)

    transicion()
    dibujarEscena()
    for f in range(ALTO):
        volcarFilas(f, f)
        time.sleep(0.012)
    time.sleep(0.25)
    ponerCara(OJ_FRENTE, BO_NEUTRAL)
    dibujarCrupier()
    volcarFilas(0, FILA_MESA)


# Si la ventana es chica para el casino, pide agrandarla (o seguir con una tecla)
#tam: terminal_size - listo: boolean

def verificarVentana():
    tam = os.get_terminal_size()
    listo = tam.columns >= ANCHO and tam.lines >= ALTO
    if listo == False:
        print("\033[0m\033[2J", end="")
    while listo == False:
        tam = os.get_terminal_size()
        print("\033[H\033[0mPara vivir el casino completo agrandá la ventana a " + str(ANCHO) + " x " + str(ALTO)
              + " (ahora: " + str(tam.columns) + " x " + str(tam.lines) + ").      \n"
              + "Se acomoda sola cuando alcance el tamaño, o presioná una tecla para seguir igual.", end="", flush=True)
        if tam.columns >= ANCHO and tam.lines >= ALTO:
            listo = True
        elif msvcrt.kbhit() == True:
            descartarTeclas()
            listo = True
        else:
            time.sleep(0.2)


def prepararConsola():
    os.system("")       # habilita los codigos de color y de cursor en la consola de Windows
    verificarVentana()
    print("\033[?25l\033[0m\033[2J", end="", flush=True)


def restaurarConsola():
    print("\033[0m\033[?25h\033[2J\033[H", end="", flush=True)


# -----------------------------------------------------------------------------
# Carteles de entrada y de salida del casino
# -----------------------------------------------------------------------------

#fase, f, c: int - fondo: int

def dibujarMarquesina(fase):
    for f in range(ALTO):
        for c in range(ANCHO):
            ponerCelda(f, c, " ", colorANSI(C_GRIS, C_NEGRO))
    for c in range(1, ANCHO - 1, 2):
        bombita(0, c, fase, C_NEGRO)
        bombita(ALTO - 1, c, fase, C_NEGRO)
    for f in range(1, ALTO - 1):
        bombita(f, 1, fase, C_NEGRO)
        bombita(f, ANCHO - 2, fase, C_NEGRO)


# Cartel "CASINO" de neon con sombra
#fila, tinta, sombra, col: int

def dibujarNeon(fila, tinta, sombra):
    col = (ANCHO - anchoGrande("CASINO", True)) // 2
    # el "resplandor" del neon: una linea tenue debajo de las letras
    for c in range(col, col + anchoGrande("CASINO", True)):
        ponerCelda(fila + 5, c, "▀", colorANSI(sombra, C_NEGRO))
    pegarGrande(fila, col, "CASINO", colorANSI(tinta, C_NEGRO), True)


#fila_ini, fila_fin, col_ini, col_fin, color: int - f, c: int

def dibujarMarco(fila_ini, fila_fin, col_ini, col_fin, color):
    borde = colorANSI(color, C_NEGRO)
    for c in range(col_ini + 1, col_fin):
        ponerCelda(fila_ini, c, "═", borde)
        ponerCelda(fila_fin, c, "═", borde)
    for f in range(fila_ini + 1, fila_fin):
        ponerCelda(f, col_ini, "║", borde)
        ponerCelda(f, col_fin, "║", borde)
    ponerCelda(fila_ini, col_ini, "╔", borde)
    ponerCelda(fila_ini, col_fin, "╗", borde)
    ponerCelda(fila_fin, col_ini, "╚", borde)
    ponerCelda(fila_fin, col_fin, "╝", borde)


#fase: int - neon: boolean - borde, texto: int

def dibujarCartelInicio(fase, neon):
    dibujarMarquesina(fase)
    if neon == True:
        dibujarNeon(3, C_NEON, 89)
    else:
        dibujarNeon(3, 53, C_NEGRO)
    pegarCentrado(10, "U T N   ·   J U E G O S   D E   A Z A R   Y   L Ó G I C A", colorANSI(C_CIAN, C_NEGRO))
    pegarCentrado(12, "♠       ♥       ♦       ♣", colorANSI(C_ORO, C_NEGRO))

    if fase % 2 == 0:
        borde = C_ROJO_VIVO
    else:
        borde = C_DORSO
    dibujarMarco(15, 21, 18, 81, borde)
    pegarCentrado(17, "!!   PROHIBIDO PARA MENORES DE 18 AÑOS   !!", colorANSI(226, C_NEGRO))
    pegarCentrado(19, "EL JUEGO COMPULSIVO ES PERJUDICIAL PARA LA SALUD", colorANSI(C_BLANCO, C_NEGRO))

    if fase % 4 < 2:
        texto = C_BLANCO
    else:
        texto = C_GRIS_OSCURO
    pegarCentrado(25, "Presioná  ENTER  para probar tu suerte", colorANSI(texto, C_NEGRO))


def cartel_inicio():
    # el neon se enciende titilando, como los carteles de verdad
    encendido = [False, True, False, False, True, False, True, True, True]
    for i in range(9):
        dibujarCartelInicio(i, encendido[i])
        volcarTodo()
        time.sleep(0.13)

    descartarTeclas()
    tecla = ""
    fase = 9
    while tecla != "\r":
        if msvcrt.kbhit() == True:
            tecla = msvcrt.getwch()
            if tecla == "\x00" or tecla == "\xe0":
                msvcrt.getwch()
                tecla = ""
        else:
            time.sleep(0.12)
            fase = fase + 1
            dibujarCartelInicio(fase, True)
            volcarTodo()


#fase, tinta, sombra: int - luces: boolean

def dibujarCartelDespedida(fase, tinta, sombra, luces):
    if luces == True:
        dibujarMarquesina(fase)
    else:
        dibujarMarquesina(-1)
    dibujarNeon(3, tinta, sombra)
    dibujarMarco(12, 19, 14, 85, C_ORO)
    pegarCentrado(14, "Gracias por jugar, no apueste, juega por diversión", colorANSI(C_ORO_CLARO, C_NEGRO))
    pegarCentrado(16, "♠   ♥   ♦   ♣", colorANSI(C_ORO_OSCURO, C_NEGRO))
    pegarCentrado(17, "MENORES DE 18 AÑOS: NO APUESTEN", colorANSI(C_ROJO_VIVO, C_NEGRO))
    if luces == True:
        pegarCentrado(24, "Presioná  ENTER  para cerrar el sistema", colorANSI(C_BLANCO, C_NEGRO))


#tecla: string - fase, i: int - colores, sombras: array de 5 int

def cartel_despedida_animado():
    transicion()
    dibujarCartelDespedida(0, C_NEON, 89, True)
    volcarTodo()
    descartarTeclas()
    tecla = ""
    fase = 0
    while tecla != "\r":
        if msvcrt.kbhit() == True:
            tecla = msvcrt.getwch()
            if tecla == "\x00" or tecla == "\xe0":
                msvcrt.getwch()
                tecla = ""
        else:
            dibujarCartelDespedida(fase, C_NEON, 89, True)
            volcarTodo()
            time.sleep(0.12)
            fase = fase + 1

    # el neon se va apagando y se cierran las luces
    colores = [C_NEON, 170, 127, 89, 53]
    sombras = [89, 53, 52, 233, C_NEGRO]
    for i in range(5):
        dibujarCartelDespedida(fase, colores[i], sombras[i], False)
        volcarTodo()
        time.sleep(0.25)
    transicion()
    restaurarConsola()


# =============================================================================
# MÓDULOS GENERALES (los usan los cuatro juegos, reciben parametros)
# =============================================================================


#mensaje, opcion1, opcion2, entrada: string
#es_valido: boolean

def validarOpcion(mensaje, opcion1, opcion2):
    global OP_elegida

    es_valido = False
    entrada = ""
    while es_valido == False:
        entrada = str(pedirEnMesa(mensaje)).upper()
        if entrada == opcion1 or entrada == opcion2:
            OP_elegida = entrada
            es_valido = True
            limpiarAviso()
        else:
            avisar(f"Error: ingreso invalido. Escriba '{opcion1}' o '{opcion2}'.")



#mensaje, texto: string - minimo, maximo: int
#es_valido: boolean

def validarNumero(mensaje, minimo, maximo):
    global NU_numero

    es_valido = False
    texto = ""
    while es_valido == False:
        texto = pedirEnMesa(mensaje)
        if texto.isdigit() == True and int(texto) >= minimo and int(texto) <= maximo:
            NU_numero = int(texto)
            es_valido = True
            limpiarAviso()
        else:
            avisar(f"Error: ingreso invalido. Escriba un numero entre {minimo} y {maximo}.")



# MÓDULOS DE LOS JUEGOS

#nro_cat, cant: int
#archivo: archivo - reg: Opcion

def contarOpcionesCategoria(nro_cat):
    cant = 0
    if os.path.exists(RUTA_OPCIONES):
        tam = os.path.getsize(RUTA_OPCIONES)
        archivo = open(RUTA_OPCIONES, "rb")
        while archivo.tell() < tam:
            reg = pickle.load(archivo)
            if reg.nro_categoria == nro_cat:
                cant = cant + 1
        archivo.close()
    return cant


#nro_cat, nro_op: int
#encontrado: boolean - reg, reg_buscado: Opcion

def buscarOpcion(nro_cat, nro_op):
    reg_buscado = Opcion()
    encontrado = False
    tam = os.path.getsize(RUTA_OPCIONES)
    archivo = open(RUTA_OPCIONES, "rb")
    while archivo.tell() < tam and encontrado == False:
        reg = pickle.load(archivo)
        if reg.nro_categoria == nro_cat and reg.nro_opcion == nro_op:
            reg_buscado = reg
            encontrado = True
    archivo.close()
    return reg_buscado


#nro_cat: int - pregunta: string - encontrada: boolean - reg: Categoria

def obtenerPregunta(nro_cat):
    pregunta = ""
    encontrada = False
    tam = os.path.getsize(RUTA_CATEGORIAS)
    archivo = open(RUTA_CATEGORIAS, "rb")
    while archivo.tell() < tam and encontrada == False:
        reg = pickle.load(archivo)
        if reg.nro_categoria == nro_cat:
            pregunta = reg.pregunta.strip()
            encontrada = True
    archivo.close()
    return pregunta


# Dice si el numero de opcion ya salio en esta partida.
# usados: array de int - cant_usados: cuantos lugares del array estan ocupados
#nro, cant_usados, i: int - usados: array de int - esta: boolean

def estaUsada(nro, usados, cant_usados):
    esta = False
    i = 0
    while i < cant_usados and esta == False:
        if usados[i] == nro:
            esta = True
        i = i + 1
    return esta


# Sortea un numero de opcion que no haya salido antes en la partida.
#cant_ops, cant_usados, nro: int - usados: array de int

def sortearOpcionNueva(cant_ops, usados, cant_usados):
    nro = random.randint(1, cant_ops)
    while estaUsada(nro, usados, cant_usados) == True:
        nro = random.randint(1, cant_ops)
    return nro


# =============================================================================
# MESA A: MENOR-MAYOR
# =============================================================================

# Un panel de opcion: tarjeta crema con el numero, el objeto y su valor
#col, numero, valor, fondo, f, c, k: int - texto, v: string

def dibujarPanelMM(col, numero, texto, valor):
    ancho = 38
    fondo = C_CREMA
    if MM_resaltar == True:
        if numero == MM_ganador or MM_ganador == 0:
            fondo = C_RETRATO
        if numero == MM_elegida:
            if MM_acerto == True:
                fondo = C_VERDE_CLARO
            else:
                fondo = C_ROJO_CLARO
    for c in range(ancho):
        ponerCelda(15, col + c, "▄", colorANSI(fondo, MESA_pano))
        for f in range(16, 22):
            ponerCelda(f, col + c, " ", colorANSI(C_NEGRO, fondo))
        ponerCelda(22, col + c, "▀", colorANSI(fondo, MESA_pano))
    for f in range(16, 23):
        ponerCelda(f, col + ancho, " ", colorANSI(C_NEGRO, MESA_sombra))

    pegarTexto(16, col + 2, " " + str(numero) + " ", colorANSI(C_BLANCO, MESA_base))
    if MM_resaltar == True and numero == MM_elegida:
        pegarTexto(16, col + ancho - 14, "TU ELECCIÓN", colorANSI(C_NEGRO, fondo))
    if MM_resaltar == True and numero == MM_ganador:
        pegarTexto(16, col + 7, "♦ MAYOR ♦", colorANSI(C_DORSO, fondo))

    partirTexto(texto, ancho - 4)
    for k in range(WR_cant):
        pegarTexto(17 + k, col + (ancho - len(WR_lineas[k])) // 2, WR_lineas[k], colorANSI(C_NEGRO, fondo))

    if MM_revelado == True:
        v = formatoMiles(valor)
    else:
        v = "?   ?   ?"
    pegarTexto(21, col + (ancho - len(v)) // 2, v, colorANSI(C_DORSO, fondo))


#i, color: int

def dibujarMM():
    if MM_apuesta > 0:
        pegarTexto(FILA_CONTENIDO, 66, "●●●", colorANSI(C_ROJO_CARTA, MESA_pano))
        pegarTexto(FILA_CONTENIDO, 70, "APUESTA: $ " + formatoMiles(MM_apuesta), colorANSI(C_ORO_CLARO, MESA_pano))
    if MM_ronda > 0:
        pegarTexto(FILA_CONTENIDO, 6, "RONDA " + str(MM_ronda) + " DE 6", colorANSI(C_ORO_CLARO, MESA_pano))
        for i in range(6):
            if MM_resultados[i] == 1:
                color = C_VERDE
            elif MM_resultados[i] == 2:
                color = C_ROJO_VIVO
            else:
                color = C_GRIS_OSCURO
            ponerCelda(FILA_CONTENIDO, 24 + i * 2, "●", colorANSI(color, MESA_pano))
        dibujarPanelMM(6 - MM_desp, 1, MM_izq, MM_vis_izq)
        dibujarPanelMM(56 + MM_desp, 2, MM_der, MM_vis_der)
        pegarTexto(18, 49, "VS", colorANSI(C_ORO_CLARO, MESA_pano))
        pegarCentrado(24, MM_pregunta[:90], colorANSI(C_ORO, MESA_pano))


# Las dos tarjetas entran deslizandose desde los costados
#k: int

def animarEntradaMM():
    global MM_desp
    for k in range(6):
        MM_desp = (5 - k) * 9
        dibujarEscena()
        volcarFilas(FILA_CONTENIDO, FILA_BARRA - 1)
        time.sleep(0.03)
    MM_desp = 0


# Los valores suben de a poco hasta el real, y recien ahi se marca el resultado
#k: int

def revelarMM():
    global MM_revelado, MM_resaltar, MM_vis_izq, MM_vis_der
    suspenso("Revelando valores")
    MM_revelado = True
    for k in range(1, 21):
        MM_vis_izq = MM_val_izq * k // 20
        MM_vis_der = MM_val_der * k // 20
        dibujarEscena()
        volcarFilas(FILA_CONTENIDO, FILA_BARRA - 1)
        time.sleep(0.04)
    MM_resaltar = True
    dibujarEscena()
    volcarTodo()


# Juega las 6 rondas de una categoria y devuelve la cantidad de aciertos.
#nro_cat, cant_ops, ronda, aciertos, lado, correcta: int
#pregunta: string - usados: array de int
#reg_actual, reg_nuevo, reg_izq, reg_der: Opcion

def jugarRondasMM(nro_cat, cant_ops):
    global MM_ronda, MM_izq, MM_der, MM_val_izq, MM_val_der, MM_vis_izq, MM_vis_der
    global MM_revelado, MM_resaltar, MM_elegida, MM_ganador, MM_acerto, MM_pregunta, MM_resultados
    usados = [0] * 7
    aciertos = 0
    pregunta = obtenerPregunta(nro_cat)

    # la primera opcion se sortea; las demas van saliendo ronda a ronda
    usados[0] = random.randint(1, cant_ops)
    reg_actual = buscarOpcion(nro_cat, usados[0])

    cerrarLista()
    MM_pregunta = pregunta
    MM_resultados = [0] * 6
    hablar("Pregunta: " + pregunta, OJ_FRENTE, BO_NEUTRAL)
    time.sleep(0.6)

    for ronda in range(1, 7):
        usados[ronda] = sortearOpcionNueva(cant_ops, usados, ronda)
        reg_nuevo = buscarOpcion(nro_cat, usados[ronda])

        # se sortea de que lado queda cada opcion para que no sea predecible
        lado = random.randint(1, 2)
        if lado == 1:
            reg_izq = reg_actual
            reg_der = reg_nuevo
        else:
            reg_izq = reg_nuevo
            reg_der = reg_actual

        MM_ronda = ronda
        MM_izq = limpiarTexto(reg_izq.objeto)
        MM_der = limpiarTexto(reg_der.objeto)
        MM_val_izq = reg_izq.valor
        MM_val_der = reg_der.valor
        MM_revelado = False
        MM_resaltar = False
        MM_elegida = 0
        animarEntradaMM()
        hablar(pregunta, OJ_FRENTE, BO_NEUTRAL)
        validarNumero("Tu respuesta (1 o 2): ", 1, 2)

        # la opcion correcta es la de mayor valor (si empatan, cualquiera suma)
        if reg_izq.valor > reg_der.valor:
            correcta = 1
        elif reg_der.valor > reg_izq.valor:
            correcta = 2
        else:
            correcta = NU_numero

        MM_elegida = NU_numero
        if reg_izq.valor > reg_der.valor:
            MM_ganador = 1
        elif reg_der.valor > reg_izq.valor:
            MM_ganador = 2
        else:
            MM_ganador = 0
        MM_acerto = NU_numero == correcta
        revelarMM()

        if NU_numero == correcta:
            aciertos = aciertos + 1
            MM_resultados[ronda - 1] = 1
            dibujarEscena()
            volcarFilas(FILA_CONTENIDO, FILA_CONTENIDO)
            decir("¡Correcto! Aciertos: " + str(aciertos), "", "", OJ_FRENTE, BO_SONRISA)
        else:
            MM_resultados[ronda - 1] = 2
            dibujarEscena()
            volcarFilas(FILA_CONTENIDO, FILA_CONTENIDO)
            decir("Incorrecto. Aciertos: " + str(aciertos), "", "", OJ_FRENTE, BO_SERIO)

        # la opcion de mayor valor sigue en juego para la proxima ronda
        if reg_izq.valor >= reg_der.valor:
            reg_actual = reg_izq
        else:
            reg_actual = reg_der

        esperarEnter("CONTINUAR")

    return aciertos


#pos, apuesta, nro_cat, cant_ops, aciertos, cant_activas, antes: int
#nombre: string - reg: Jugador

def EjecutarJuegoMenorMayor():
    global MM_apuesta, MM_ronda, ES_banner_fila
    MM_apuesta = 0
    MM_ronda = 0
    abrirMesa(PANT_MM, "♦  M E S A   M E N O R  -  M A Y O R  ♦")
    decir("Bienvenido a la mesa de Menor-Mayor.", "Seis rondas: elegí siempre la opción de mayor valor.",
          "Con 4 aciertos o más, ganás.", OJ_FRENTE, BO_SONRISA)
    identificarJugador()
    nombre = JU_nombre
    pos = JU_pos

    reg = leerJugador(pos)
    ponerInfo(infoCredito(nombre, int(reg.creditos)))
    if reg.creditos < 1:
        hablar(nombre + ", te quedaste sin crédito. Ya no podés jugar.", OJ_FRENTE, BO_SERIO)
    else:
        decir("Tu crédito es: $ " + formatoMiles(int(reg.creditos)), "¿Cuántos créditos apostás?", "", OJ_FRENTE, BO_PICARO)
        validarNumero(f"¿Cuantos creditos queres apostar? (1 a {int(reg.creditos)}): ", 1, int(reg.creditos))
        apuesta = NU_numero
        MM_apuesta = apuesta

        cant_activas = mostrarCategoriasActivas()
        if cant_activas == 0:
            hablar("No hay categorías activas. Cargalas desde Administración de Juegos.", OJ_FRENTE, BO_SERIO)
        else:
            decir("Apostaste $ " + formatoMiles(apuesta) + ".", "Elegí una categoría de la lista.", "", OJ_FRENTE, BO_NEUTRAL)
            validarNumero("Elegi el N° de categoria: ", 1, obtenerUltimoNroCategoria())
            nro_cat = NU_numero

            if esCategoriaActiva(nro_cat) == False:
                hablar("Error: esa categoría no existe o no está activa.", OJ_FRENTE, BO_SERIO)
            else:
                cant_ops = contarOpcionesCategoria(nro_cat)
                if cant_ops < 7:
                    hablar("Esa categoría tiene " + str(cant_ops) + " opciones y se necesitan al menos 7 para jugar.",
                           OJ_FRENTE, BO_SERIO)
                else:
                    aciertos = jugarRondasMM(nro_cat, cant_ops)

                    ES_banner_fila = 23
                    antes = int(leerJugador(pos).creditos)
                    if aciertos >= 4:
                        registrarResultado(pos, MAYOR_MENOR, True, apuesta)
                        celebrarResultado(True, "♦ ♦ ♦     G A N A S T E   ·   " + str(aciertos) + "  D E  6     ♦ ♦ ♦")
                        hablar("Terminaste con " + str(aciertos) + " aciertos de 6. ¡GANASTE " + nombre + "! Sumaste $ "
                               + formatoMiles(apuesta) + ".", OJ_FRENTE, BO_SORPRESA)
                    else:
                        registrarResultado(pos, MAYOR_MENOR, False, -apuesta)
                        celebrarResultado(False, "♦ ♦ ♦     P E R D I S T E   ·   " + str(aciertos) + "  D E  6     ♦ ♦ ♦")
                        hablar("Terminaste con " + str(aciertos) + " aciertos de 6. Perdiste. Se descuentan $ "
                               + formatoMiles(apuesta) + ".", OJ_GUINO, BO_PICARO)

                    reg = leerJugador(pos)
                    animarCredito(nombre, antes, int(reg.creditos))


# =============================================================================
# MESA B: NUMERO SECRETO
# =============================================================================

#i, n, col, color, ancho: int - pista, texto: string

def dibujarNS():
    if NS_activo == True:
        # la boveda con el numero escondido
        pegarCentrado(FILA_CONTENIDO, "♦   B Ó V E D A   ♦", colorANSI(C_ORO_CLARO, MESA_pano))
        dibujarMarcoMesa(14, 20, 38, 61, C_ORO)
        for i in range(15, 20):
            for col in range(39, 61):
                ponerCelda(i, col, " ", colorANSI(C_GRIS, C_NEGRO))
        if NS_revelado == False:
            color = C_DORSO
        elif NS_adivino == True:
            color = C_VERDE
        else:
            color = C_ROJO_VIVO
        ancho = anchoGrande(NS_display, False)
        pegarGrande(15, 50 - ancho // 2, NS_display, colorANSI(color, C_NEGRO), False)

        # intentos que quedan
        pegarTexto(15, 70, "INTENTOS", colorANSI(C_ORO_CLARO, MESA_pano))
        for i in range(5):
            if i < NS_restantes:
                color = 226
            else:
                color = C_GRIS_OSCURO
            ponerCelda(16, 70 + i * 2, "●", colorANSI(color, MESA_pano))
        pegarTexto(17, 70, "Quedan " + str(NS_restantes), colorANSI(C_GRIS, MESA_pano))

        # el ultimo numero y la pista
        if NS_ultimo > 0:
            pegarTexto(14, 8, "TU NÚMERO", colorANSI(C_ORO_CLARO, MESA_pano))
            pegarGrande(15, 8, str(NS_ultimo), colorANSI(C_BLANCO, MESA_pano), False)
            if NS_pista == 1:
                pegarTexto(21, 8, "▲  ES MAYOR", colorANSI(C_VERDE, MESA_pano))
            elif NS_pista == 2:
                pegarTexto(21, 8, "▼  ES MENOR", colorANSI(C_NARANJA, MESA_pano))

        # regla del 1 al 100: en claro, donde todavia puede estar el numero
        for i in range(50):
            n = i * 2 + 1
            if n + 1 >= NS_min and n <= NS_max:
                ponerCelda(23, 25 + i, "█", colorANSI(44, MESA_pano))
            else:
                ponerCelda(23, 25 + i, "░", colorANSI(C_GRIS_OSCURO, MESA_pano))
        if NS_ultimo > 0:
            ponerCelda(22, 25 + (NS_ultimo - 1) // 2, "▼", colorANSI(C_ORO_CLARO, MESA_pano))
        pegarTexto(24, 25, "1", colorANSI(C_GRIS, MESA_pano))
        pegarTexto(24, 49, "50", colorANSI(C_GRIS, MESA_pano))
        pegarTexto(24, 72, "100", colorANSI(C_GRIS, MESA_pano))


# Marco de linea doble sobre el paño
#fila_ini, fila_fin, col_ini, col_fin, color, f, c: int - borde: string

def dibujarMarcoMesa(fila_ini, fila_fin, col_ini, col_fin, color):
    borde = colorANSI(color, MESA_pano)
    for c in range(col_ini + 1, col_fin):
        ponerCelda(fila_ini, c, "═", borde)
        ponerCelda(fila_fin, c, "═", borde)
    for f in range(fila_ini + 1, fila_fin):
        ponerCelda(f, col_ini, "║", borde)
        ponerCelda(f, col_fin, "║", borde)
    ponerCelda(fila_ini, col_ini, "╔", borde)
    ponerCelda(fila_ini, col_fin, "╗", borde)
    ponerCelda(fila_fin, col_ini, "╚", borde)
    ponerCelda(fila_fin, col_fin, "╝", borde)


# La combinacion de la boveda gira hasta frenar en el numero secreto
#numero, k: int

def abrirBoveda(numero):
    global NS_display, NS_revelado
    for k in range(18):
        NS_display = str(random.randint(1, 100))
        dibujarEscena()
        volcarFilas(FILA_CONTENIDO, FILA_BARRA - 1)
        time.sleep(0.03 + k * 0.007)
    NS_display = str(numero)
    NS_revelado = True
    dibujarEscena()
    volcarTodo()


#numero_secreto, intentos, pos: int
#nombre: string
#adivino: boolean

def nro_secreto():
    global NS_activo, NS_min, NS_max, NS_ultimo, NS_pista, NS_restantes, NS_display, NS_revelado, NS_adivino
    global ES_banner_fila
    NS_activo = False
    abrirMesa(PANT_NS, "♦  L A   B Ó V E D A   ·   N Ú M E R O   S E C R E T O  ♦")
    decir("Esta es la bóveda del casino.", "La combinación es un número del 1 al 100.", "Tenés 5 intentos para abrirla.",
          OJ_FRENTE, BO_PICARO)
    identificarJugador()
    nombre = JU_nombre
    pos = JU_pos
    ponerInfo(infoCredito(nombre, int(leerJugador(pos).creditos)))

    numero_secreto = random.randint(1, 100)
    intentos = 1
    adivino = False

    NS_activo = True
    NS_min = 1
    NS_max = 100
    NS_ultimo = 0
    NS_pista = 0
    NS_restantes = 5
    NS_display = "???"
    NS_revelado = False
    NS_adivino = False
    mostrarEnMesa()
    decir("Ya pensé el número.", "Piense un número entre 1 y 100.", "Tenés 5 intentos para adivinarlo.", OJ_GUINO, BO_PICARO)

    while intentos <= 5 and adivino == False:
        NS_restantes = 6 - intentos
        mostrarEnMesa()
        decir("Intento " + str(intentos) + " de 5. Te quedan " + str(6 - intentos) + " intentos.", "", "",
              OJ_FRENTE, BO_NEUTRAL)
        validarNumero("Ingresar un numero entre 1 y 100: ", 1, 100)
        NS_ultimo = NU_numero

        if NU_numero == numero_secreto:
            adivino = True
        else:
            suspenso("Probando la combinación")
            if NU_numero < numero_secreto:
                NS_pista = 1
                if NU_numero + 1 > NS_min:
                    NS_min = NU_numero + 1
                mostrarEnMesa()
                decir("Pista: El número secreto es MAYOR.", "", "", OJ_FRENTE, BO_PICARO)
            else:
                NS_pista = 2
                if NU_numero - 1 < NS_max:
                    NS_max = NU_numero - 1
                mostrarEnMesa()
                decir("Pista: El número secreto es MENOR.", "", "", OJ_FRENTE, BO_PICARO)
            intentos = intentos + 1
            time.sleep(0.5)

    NS_restantes = 6 - intentos
    if adivino == False:
        NS_restantes = 0
    NS_adivino = adivino
    NS_pista = 0
    ES_banner_fila = 22
    suspenso("Abriendo la bóveda")
    abrirBoveda(numero_secreto)
    if adivino == True:
        celebrarResultado(True, "♦ ♦ ♦     B Ó V E D A   A B I E R T A     ♦ ♦ ♦")
        hablar("¡FELICIDADES " + nombre + "! Adivinaste en " + str(intentos) + " intentos.", OJ_FRENTE, BO_SORPRESA)
        registrarResultado(pos, NUM_SECRETO, True, 0)
    else:
        celebrarResultado(False, "♦ ♦ ♦     P E R D I S T E     ♦ ♦ ♦")
        hablar("PERDISTE. El número secreto era: " + str(numero_secreto), OJ_GUINO, BO_PICARO)
        registrarResultado(pos, NUM_SECRETO, False, 0)


# =============================================================================
# MESA C: BLACKJACK
# =============================================================================

#c, f: int

def dibujarZapato():
    for c in range(ZA_COL - 1, ZA_COL + 9):
        ponerCelda(ZA_FILA - 1, c, "▄", colorANSI(C_MADERA, fondoFila(ZA_FILA - 1)))
        for f in range(ZA_FILA, ZA_FILA + 4):
            ponerCelda(f, c, " ", colorANSI(C_MADERA_CLARA, C_MADERA))
        ponerCelda(ZA_FILA + 4, c, "▀", colorANSI(C_MADERA, fondoFila(ZA_FILA + 4)))
    for f in range(ZA_FILA, ZA_FILA + 3):
        for c in range(ZA_COL + 1, ZA_COL + 7):
            ponerCelda(f, c, "▒", colorANSI(C_DORSO_DIBUJO, C_DORSO))
    pegarTexto(ZA_FILA + 5, ZA_COL - 1, "Quedan " + str(52 - BJ_usadas), colorANSI(C_ORO_OSCURO, MESA_pano))


# Pilas de fichas de la casa, al lado del zapato. Cada celda muestra 2 fichas
# (con ▀) y la columna del medio es el borde blanco, como en las fichas reales.
#i, f, c, col, alto, color: int - colores, oscuros, altos: array de 3 int

def dibujarFichas():
    colores = [160, 33, 178]
    oscuros = [88, 18, 136]
    altos = [3, 4, 2]
    for i in range(3):
        col = 74 + i * 4
        alto = altos[i]
        for c in range(3):
            color = colores[i]
            if c == 1:
                color = C_BLANCO
            ponerCelda(19 - alto, col + c, "▄", colorANSI(colores[i], MESA_pano))
            for f in range(20 - alto, 20):
                ponerCelda(f, col + c, "▀", colorANSI(color, oscuros[i]))
            ponerCelda(20, col + c, "▀", colorANSI(MESA_sombra, MESA_pano))


# La leyenda impresa en el paño (cuando no hay cartel de resultado)

def dibujarLeyenda():
    if ES_banner == "":
        pegarCentrado(FILA_LEYENDA, "♠ ♥   B L A C K J A C K   ♦ ♣      La banca pide con 16 y se planta con 17",
                      colorANSI(C_ORO_OSCURO, MESA_pano))


#id_carta: int

def figuraDeCarta(id_carta):
    return (id_carta - 1) % 13 + 1


#id_carta: int

def paloDeCarta(id_carta):
    return (id_carta - 1) // 13


#id_carta: int

def valorDeCarta(id_carta):
    return BJ_VALORES[figuraDeCarta(id_carta)]


# Centro de las J, Q y K: un retrato con corona
#fila, izq, tinta, f, c: int - rango, simbolo, marco, corona: string

def dibujarRetrato(fila, izq, rango, simbolo, tinta):
    marco = colorANSI(tinta, C_RETRATO)
    for f in range(1, 6):
        for c in range(2, 7):
            ponerCelda(fila + f, izq + c, " ", marco)
    if rango == "K":
        corona = "▲▲▲"
    elif rango == "Q":
        corona = "♦▲♦"
    else:
        corona = " ▲ "
    pegarTexto(fila + 2, izq + 3, corona, colorANSI(C_ORO, C_RETRATO))
    pegarTexto(fila + 3, izq + 4, rango, marco)
    pegarTexto(fila + 4, izq + 4, simbolo, marco)


# Dibuja una carta de 9 x 7 con su sombra. Con ancho menor a 9 se dibuja
# "de canto" (sirve para la animacion de darla vuelta).
#fila, col, id_carta, ancho, izq, f, c, k, palo, figura, tinta: int
#boca_arriba: boolean - color, rango, simbolo, pintas: string

def dibujarCarta(fila, col, id_carta, boca_arriba, ancho):
    izq = col + (9 - ancho) // 2
    for f in range(fila + 1, fila + 7):
        ponerCelda(f, izq + ancho, " ", colorANSI(C_NEGRO, MESA_sombra))

    if boca_arriba == True:
        palo = paloDeCarta(id_carta)
        figura = figuraDeCarta(id_carta)
        if palo == 1 or palo == 2:
            tinta = C_ROJO_CARTA
        else:
            tinta = C_NEGRO
        color = colorANSI(tinta, C_BLANCO)
        for f in range(7):
            for c in range(ancho):
                ponerCelda(fila + f, izq + c, " ", color)

        if ancho == 9:
            rango = BJ_FIGURAS[figura]
            simbolo = BJ_SIMBOLOS[palo]
            pegarTexto(fila, izq + 1, rango, color)
            pegarTexto(fila + 6, izq + 8 - len(rango), rango, color)
            if figura >= 11:
                dibujarRetrato(fila, izq, rango, simbolo, tinta)
            else:
                pintas = BJ_PINTAS[figura]
                for k in range(len(pintas) // 2):
                    pegarTexto(fila + int(pintas[2 * k]), izq + int(pintas[2 * k + 1]), simbolo, color)
    else:
        for f in range(7):
            for c in range(ancho):
                if f == 0 or f == 6 or c == 0 or c == ancho - 1:
                    ponerCelda(fila + f, izq + c, " ", colorANSI(C_BLANCO, C_BLANCO))
                else:
                    ponerCelda(fila + f, izq + c, "▒", colorANSI(C_DORSO_DIBUJO, C_DORSO))


# Separacion entre cartas: si la mano crece mucho se superponen un poco
#cant, paso: int

def pasoMano(cant):
    paso = 10
    if cant > 7:
        paso = 60 // (cant - 1)
    return paso


# Deja en PC_fila y PC_col donde va la carta numero "indice" de una mano de "cant" cartas
#quien, indice, cant: int

def posicionCarta(quien, indice, cant):
    global PC_fila, PC_col
    if quien == BANCA:
        PC_fila = 14
    else:
        PC_fila = 22
    PC_col = 18 + indice * pasoMano(cant)


#quien, i: int - boca_arriba: boolean

def dibujarManos():
    for quien in range(2):
        for i in range(BJ_cant_cartas[quien]):
            if quien != ES_omitir_quien or i != ES_omitir_indice:
                posicionCarta(quien, i, BJ_cant_cartas[quien])
                boca_arriba = True
                if quien == BANCA and i == 1 and ES_oculta == True:
                    boca_arriba = False
                dibujarCarta(PC_fila, PC_col, BJ_ids[quien][i], boca_arriba, 9)


#fila, col, izq, color_valor: int - titulo, valor, oro: string

def dibujarCaja(fila, col, titulo, valor, color_valor):
    oro = colorANSI(C_ORO, MESA_pano)
    pegarTexto(fila, col, titulo, colorANSI(C_ORO_CLARO, MESA_pano))
    pegarTexto(fila + 2, col, "┌──────┐", oro)
    pegarTexto(fila + 3, col, "│", oro)
    izq = (6 - len(valor)) // 2
    pegarTexto(fila + 3, col + 1, " " * izq + valor + " " * (6 - izq - len(valor)), colorANSI(color_valor, MESA_pano))
    pegarTexto(fila + 3, col + 7, "│", oro)
    pegarTexto(fila + 4, col, "└──────┘", oro)


#total, color: int

def colorTotal(total):
    if total > 21:
        color = C_ROJO_VIVO
    elif total == 21:
        color = C_ORO_CLARO
    else:
        color = C_BLANCO
    return color


#valor: string

def dibujarTotales():
    if BJ_cant_cartas[BANCA] == 0:
        valor = ""
    elif ES_oculta == True:
        valor = str(valorDeCarta(BJ_ids[BANCA][0])) + " + ?"
    else:
        valor = str(BJ_totales[BANCA])
    dibujarCaja(14, 3, "BANCA", valor, colorTotal(BJ_totales[BANCA]))

    if BJ_cant_cartas[JUGADOR] == 0:
        valor = ""
    else:
        valor = str(BJ_totales[JUGADOR])
    dibujarCaja(22, 3, ES_nombre[:14], valor, colorTotal(BJ_totales[JUGADOR]))


# Da vuelta una carta: se angosta hasta quedar de canto y vuelve a abrirse
# mostrando la cara. En el medio del giro se levanta una fila del paño.
#fila, col, id_carta, i, levantar: int - demora: float - anchos: array de 8 int

def animarVolteo(fila, col, id_carta, demora):
    anchos = [7, 5, 3, 1, 3, 5, 7, 9]
    for i in range(8):
        levantar = 0
        if i >= 1 and i <= 5:
            levantar = 1
        dibujarEscena()
        dibujarCarta(fila - levantar, col, id_carta, i >= 4, anchos[i])
        volcarFilas(FILA_MESA + 1, FILA_BARRA - 1)
        time.sleep(demora)


# La carta sale del zapato boca abajo y viaja hasta su lugar en la mano.
# El croupier la sigue con la mirada.
#quien, id_carta, indice, destino_f, destino_c, p, f, c: int - boca_arriba: boolean

def animarVuelo(quien, id_carta, boca_arriba):
    indice = BJ_cant_cartas[quien]
    posicionCarta(quien, indice, indice + 1)
    destino_f = PC_fila
    destino_c = PC_col

    for p in range(1, 10):
        f = ZA_FILA + (destino_f - ZA_FILA) * p // 9
        c = ZA_COL + (destino_c - ZA_COL) * p // 9
        if c > 60:
            ponerCara(OJ_DER, CR_boca)
        elif c < 40:
            ponerCara(OJ_IZQ, CR_boca)
        else:
            ponerCara(OJ_FRENTE, CR_boca)
        dibujarEscena()
        dibujarCarta(f, c, id_carta, False, 9)
        volcarFilas(0, FILA_BARRA - 1)
        time.sleep(0.016)

    if boca_arriba == True:
        animarVolteo(destino_f, destino_c, id_carta, 0.035)
    ponerCara(OJ_FRENTE, CR_boca)


# Mezcla: dos medios mazos se juntan intercalando cartas y despues van al zapato
#vuelta, paso, sep, p, f, c: int

def animarMezcla():
    for vuelta in range(3):
        for paso in range(7):
            if paso <= 3:
                sep = 3 - paso
            else:
                sep = paso - 3
            dibujarEscena()
            dibujarCarta(16 - paso % 2, 41 - sep * 4, 0, False, 9)
            dibujarCarta(16 - paso % 2, 40 - sep * 4, 0, False, 9)
            dibujarCarta(16 - (paso + 1) % 2, 51 + sep * 4, 0, False, 9)
            dibujarCarta(16 - (paso + 1) % 2, 50 + sep * 4, 0, False, 9)
            volcarFilas(FILA_MESA + 1, FILA_BARRA - 1)
            time.sleep(0.05)

    for p in range(1, 9):
        f = 16 + (ZA_FILA - 16) * p // 8
        c = 45 + (ZA_COL - 45) * p // 8
        dibujarEscena()
        dibujarCarta(f, c, 0, False, 9)
        volcarFilas(FILA_MESA + 1, FILA_BARRA - 1)
        time.sleep(0.03)
    dibujarEscena()
    volcarTodo()


#i: int

def mezclarMazoBJ():
    global BJ_usadas

    # las 52 cartas vuelven a estar sin usar
    for i in range(1, 53):
        BJ_mazo[i] = False
    BJ_usadas = 0

    for i in range(2):
        BJ_cant_cartas[i] = 0
        BJ_totales[i] = 0
        BJ_ases[i] = 0


#figura: int

def repartirCartaBJ():
    global BJ_id_carta, BJ_valor_carta, BJ_es_as, BJ_usadas

    # se sortea una carta del 1 al 52 hasta que salga una que no haya salido antes
    BJ_id_carta = random.randint(1, 52)
    while BJ_mazo[BJ_id_carta] == True:
        BJ_id_carta = random.randint(1, 52)
    BJ_mazo[BJ_id_carta] = True
    BJ_usadas = BJ_usadas + 1

    figura = figuraDeCarta(BJ_id_carta)
    BJ_valor_carta = BJ_VALORES[figura]
    if figura == 1:
        BJ_es_as = True
    else:
        BJ_es_as = False


# Saca una carta del mazo, la anima hasta la mano y actualiza el total
#quien: int - boca_arriba: boolean

def agregarCartaBJ(quien, boca_arriba):
    repartirCartaBJ()
    animarVuelo(quien, BJ_id_carta, boca_arriba)

    BJ_ids[quien][BJ_cant_cartas[quien]] = BJ_id_carta
    BJ_cant_cartas[quien] = BJ_cant_cartas[quien] + 1
    BJ_totales[quien] = BJ_totales[quien] + BJ_valor_carta
    if BJ_es_as == True:
        BJ_ases[quien] = BJ_ases[quien] + 1

    # cada As que estaba valiendo 11 pasa a valer 1 (se restan 10)
    while BJ_totales[quien] > 21 and BJ_ases[quien] > 0:
        BJ_totales[quien] = BJ_totales[quien] - 10
        BJ_ases[quien] = BJ_ases[quien] - 1

    dibujarEscena()
    volcarTodo()


#demora: float

def revelarCartaOculta(demora):
    global ES_oculta, ES_omitir_quien, ES_omitir_indice
    posicionCarta(BANCA, 1, BJ_cant_cartas[BANCA])
    ES_omitir_quien = BANCA
    ES_omitir_indice = 1
    ES_oculta = False
    animarVolteo(PC_fila, PC_col, BJ_ids[BANCA][1], demora)
    ES_omitir_quien = -1
    ES_omitir_indice = -1
    dibujarEscena()
    volcarTodo()


#sigue_pidiendo: boolean

def turnoJugadorBJ():
    if BJ_totales[JUGADOR] == 21:
        decir("¡Blackjack! 21 con las dos primeras cartas.", "Eso no se ve todos los días...", "", OJ_FRENTE, BO_SORPRESA)
        time.sleep(0.8)

    sigue_pidiendo = True
    while BJ_totales[JUGADOR] < 21 and sigue_pidiendo == True:
        decir("Tenés " + str(BJ_totales[JUGADOR]) + ". La banca muestra " + str(valorDeCarta(BJ_ids[BANCA][0])) + ".",
              "¿Pedís otra carta o te plantás?", "", OJ_FRENTE, BO_NEUTRAL)
        mostrarBotones("P", "PEDIR CARTA", "M", "ME PLANTO")
        esperarTecla("P", "M")
        mostrarBotones("", "", "", "")

        if TE_tecla == "P":
            decir(FR_PEDIR[random.randint(0, 4)], "", "", OJ_DER, BO_PICARO)
            agregarCartaBJ(JUGADOR, True)
            if BJ_totales[JUGADOR] > 21:
                decir("Uh... " + str(BJ_totales[JUGADOR]) + ". Te pasaste.", "", "", OJ_FRENTE, BO_SERIO)
                time.sleep(0.7)
            elif BJ_totales[JUGADOR] == 21:
                decir("¡21 justos!", "Ahora me toca a mí...", "", OJ_FRENTE, BO_SORPRESA)
                time.sleep(0.7)
        else:
            sigue_pidiendo = False
            decir("Te plantás con " + str(BJ_totales[JUGADOR]) + ". Respetable.", "", "", OJ_FRENTE, BO_NEUTRAL)
            time.sleep(0.5)


def turnoBancaBJ():
    if BJ_totales[JUGADOR] > 21:
        # el jugador ya perdio: la banca no pide, solo muestra su carta
        decir("La banca no necesita jugar.", "Igual te muestro lo que tenía...", "", OJ_FRENTE, BO_PICARO)
        revelarCartaOculta(0.04)
    else:
        decir("Muy bien... es mi turno.", "Veamos qué escondía la banca.", "", OJ_FRENTE, BO_NEUTRAL)
        suspenso("Dando vuelta la carta")
        revelarCartaOculta(0.09)
        time.sleep(0.4)
        decir("La banca tiene " + str(BJ_totales[BANCA]) + ".", "", "", OJ_FRENTE, BO_NEUTRAL)
        time.sleep(0.6)

        # la banca pide carta con 16 o menos y se planta con 17 o mas
        while BJ_totales[BANCA] < 17:
            decir("Con " + str(BJ_totales[BANCA]) + " la regla me obliga a pedir...", "", "", OJ_DER, BO_SERIO)
            suspenso("La banca pide carta")
            agregarCartaBJ(BANCA, True)
            time.sleep(0.4)


#nombre: string - pos: int

def infoBlackjack(nombre, pos):
    reg = leerJugador(pos)
    ponerInfo("Jugador: " + nombre[:14] + "   ·   Ganadas: " + str(reg.juegos[GANADAS][BLACKJACK])
              + "   ·   Perdidas: " + str(reg.juegos[PERDIDAS][BLACKJACK]))


#nombre: string - pos, jugador, banca: int

def resultadoBJ(nombre, pos):
    global ES_banner_fila
    jugador = BJ_totales[JUGADOR]
    banca = BJ_totales[BANCA]
    ES_banner_fila = FILA_LEYENDA

    if jugador > 21:
        registrarResultado(pos, BLACKJACK, False, 0)
        celebrar("♦ ♦ ♦     L A   C A S A   G A N A     ♦ ♦ ♦", C_BLANCO, C_DORSO, 52)
        decir("Te pasaste de 21. La casa gana esta vez.", "Siempre hay revancha...", "", OJ_GUINO, BO_PICARO)
    elif banca > 21:
        registrarResultado(pos, BLACKJACK, True, 0)
        celebrar("♦ ♦ ♦     G A N A S T E     ♦ ♦ ♦", C_NEGRO, C_ORO_CLARO, 34)
        decir("¡Me pasé con " + str(banca) + "!", "La mano es tuya, " + nombre + ".", "", OJ_FRENTE, BO_SORPRESA)
    elif jugador > banca:
        registrarResultado(pos, BLACKJACK, True, 0)
        celebrar("♦ ♦ ♦     G A N A S T E     ♦ ♦ ♦", C_NEGRO, C_ORO_CLARO, 34)
        decir("Bien jugado, " + nombre + ".", str(jugador) + " contra " + str(banca) + ". Ganaste.", "", OJ_FRENTE, BO_SONRISA)
    elif jugador == banca:
        celebrar("♦ ♦ ♦     E M P A T E     ♦ ♦ ♦", C_NEGRO, C_GRIS, 24)
        decir("Empate en " + str(jugador) + ".", "Nadie se lleva nada esta vez.", "", OJ_FRENTE, BO_NEUTRAL)
    else:
        registrarResultado(pos, BLACKJACK, False, 0)
        celebrar("♦ ♦ ♦     L A   C A S A   G A N A     ♦ ♦ ♦", C_BLANCO, C_DORSO, 52)
        decir(str(banca) + " contra " + str(jugador) + ". La casa gana.", "¿Te animás a la revancha?", "", OJ_GUINO, BO_PICARO)

    infoBlackjack(nombre, pos)


#nombre: string - pos, i: int

def jugarManoBJ(nombre, pos):
    global ES_oculta, ES_banner
    mezclarMazoBJ()
    ES_oculta = True
    ES_banner = ""
    dibujarEscena()
    volcarTodo()

    decir("Mazo nuevo de 52 cartas. Sin trampas...", "Mezclando.", "", OJ_GUINO, BO_PICARO)
    animarMezcla()
    decir("Hagan juego...", "", "", OJ_FRENTE, BO_NEUTRAL)

    # reparto: jugador, banca, jugador, banca (la segunda de la banca boca abajo)
    for i in range(2):
        agregarCartaBJ(JUGADOR, True)
        agregarCartaBJ(BANCA, i == 0)

    turnoJugadorBJ()
    turnoBancaBJ()
    resultadoBJ(nombre, pos)


#pos: int
#nombre: string
#sigue_partida: boolean

def blackjack():
    mezclarMazoBJ()
    abrirMesa(PANT_BJ, "♦  M E S A   2 1   ·   B L A C K J A C K  ♦")
    decir("Buenas noches. Bienvenido a la mesa de Blackjack.", "Antes de repartir, decime tu nombre.", "",
          OJ_FRENTE, BO_SONRISA)
    identificarJugador()
    nombre = JU_nombre
    pos = JU_pos
    infoBlackjack(nombre, pos)
    time.sleep(0.6)
    decir("Las reglas son simples: llegá a 21 sin pasarte.", "Las figuras valen 10 y el As vale 1 u 11.",
          "Yo pido con 16 o menos y me planto con 17.", OJ_FRENTE, BO_NEUTRAL)
    time.sleep(0.9)

    sigue_partida = True
    while sigue_partida == True:
        jugarManoBJ(nombre, pos)

        # --- CONSULTA OTRA PARTIDA ---
        decir("¿Jugamos otra mano?", "", "", OJ_FRENTE, BO_SONRISA)
        mostrarBotones("S", "OTRA MANO", "N", "TERMINAR")
        esperarTecla("S", "N")
        mostrarBotones("", "", "", "")
        if TE_tecla == "N":
            sigue_partida = False

    decir("Gracias por jugar, " + nombre + ".", "Recordá: jugá por diversión, nunca por necesidad.", "", OJ_GUINO, BO_SONRISA)


# =============================================================================
# MESA D: PAR O IMPAR
# =============================================================================

# Un dado de 11 x 5 con su sombra. Cara 0 = todavia no se tiro (muestra ?)
#fila, col, cara, fondo, f, c, k, tinta: int - puntos: string

def dibujarDado(fila, col, cara):
    for f in range(fila + 1, fila + 5):
        ponerCelda(f, col + 11, " ", colorANSI(C_NEGRO, MESA_sombra))
    for c in range(col + 1, col + 12):
        ponerCelda(fila + 5, c, "▀", colorANSI(MESA_sombra, MESA_pano))
    if cara == 0:
        fondo = C_GRIS
    else:
        fondo = C_BLANCO
    for f in range(5):
        for c in range(11):
            ponerCelda(fila + f, col + c, " ", colorANSI(C_NEGRO, fondo))
    if cara == 0:
        ponerCelda(fila + 2, col + 5, "?", colorANSI(C_NEGRO, fondo))
    else:
        tinta = C_NEGRO
        if cara == 1:
            tinta = C_ROJO_CARTA
        puntos = PI_PUNTOS[cara]
        for k in range(len(puntos) // 2):
            ponerCelda(fila + 1 + int(puntos[2 * k]), col + 2 + int(puntos[2 * k + 1]) * 3, "●", colorANSI(tinta, fondo))


def dibujarPI():
    if PI_apuesta > 0:
        pegarTexto(15, 6, "APUESTA", colorANSI(C_ORO_CLARO, MESA_pano))
        pegarTexto(16, 6, "●●● $ " + formatoMiles(PI_apuesta), colorANSI(C_BLANCO, MESA_pano))
    if PI_eleccion != "":
        pegarTexto(18, 6, "TU JUGADA", colorANSI(C_ORO_CLARO, MESA_pano))
        pegarTexto(19, 6, PI_eleccion, colorANSI(C_BLANCO, MESA_pano))
    pegarCentrado(FILA_CONTENIDO, "♦   D A D O S   ·   P A R   O   I M P A R   ♦", colorANSI(C_ORO_CLARO, MESA_pano))
    dibujarDado(15 + PI_salto1, 36 + PI_corr1, PI_dado1)
    dibujarDado(15 + PI_salto2, 54 + PI_corr2, PI_dado2)
    if PI_suma > 0:
        pegarCentrado(21, str(PI_dado1) + "   +   " + str(PI_dado2) + "   =   " + str(PI_suma) + "        ·        "
                      + PI_resultado, colorANSI(C_ORO_CLARO, MESA_pano))


# Los dados ruedan sobre el paño, cada vez mas lento, hasta frenar
#num1, num2, k: int

def animarDados(num1, num2):
    global PI_dado1, PI_dado2, PI_salto1, PI_salto2, PI_corr1, PI_corr2
    for k in range(16):
        PI_dado1 = random.randint(1, 6)
        PI_dado2 = random.randint(1, 6)
        PI_salto1 = random.randint(-1, 1)
        PI_salto2 = random.randint(-1, 1)
        PI_corr1 = random.randint(-3, 3)
        PI_corr2 = random.randint(-3, 3)
        if k % 2 == 0:
            ponerCara(OJ_IZQ, BO_SORPRESA)
        else:
            ponerCara(OJ_DER, BO_SORPRESA)
        dibujarEscena()
        volcarFilas(0, FILA_BARRA - 1)
        time.sleep(0.04 + k * 0.012)
    PI_dado1 = num1
    PI_dado2 = num2
    PI_salto1 = 0
    PI_salto2 = 0
    PI_corr1 = 0
    PI_corr2 = 0
    ponerCara(OJ_FRENTE, BO_NEUTRAL)
    dibujarEscena()
    volcarTodo()


#nombre, resultado: string
#pos, num1, num2, suma, apuesta, antes: int
#reg: Jugador

def par_impar():
    global PI_dado1, PI_dado2, PI_apuesta, PI_suma, PI_eleccion, PI_resultado, ES_banner_fila
    PI_dado1 = 0
    PI_dado2 = 0
    PI_apuesta = 0
    PI_suma = 0
    PI_eleccion = ""
    PI_resultado = ""
    abrirMesa(PANT_PI, "♦  M E S A   D E   D A D O S  ·  P A R   O   I M P A R  ♦")
    decir("Bienvenido a la mesa de dados.", "Tiro dos dados: vos adivinás si la suma es par o impar.", "",
          OJ_FRENTE, BO_SONRISA)
    identificarJugador()
    nombre = JU_nombre
    pos = JU_pos

    reg = leerJugador(pos)
    ponerInfo(infoCredito(nombre, int(reg.creditos)))
    if reg.creditos < 1:
        hablar(nombre + ", te quedaste sin crédito. Ya no podés jugar.", OJ_FRENTE, BO_SERIO)
    else:
        decir("Tu crédito es: $ " + formatoMiles(int(reg.creditos)), "¿Cuánto apostás?", "", OJ_FRENTE, BO_PICARO)
        validarNumero(f"Cuanto apostas? (1 a {int(reg.creditos)}): ", 1, int(reg.creditos))
        apuesta = NU_numero
        PI_apuesta = apuesta
        mostrarEnMesa()
        decir("$ " + formatoMiles(apuesta) + " sobre la mesa.", "¿La suma va a ser PAR o IMPAR?", "", OJ_FRENTE, BO_NEUTRAL)
        validarOpcion("El numero es par o impar? : ", "PAR", "IMPAR")
        PI_eleccion = OP_elegida

        num1 = random.randint(1, 6)
        num2 = random.randint(1, 6)
        suma = num1 + num2
        if suma % 2 == 0:
            resultado = "PAR"
        else:
            resultado = "IMPAR"

        mostrarEnMesa()
        decir("No va más...", "", "", OJ_FRENTE, BO_PICARO)
        animarDados(num1, num2)
        PI_suma = suma
        PI_resultado = resultado
        mostrarEnMesa()
        decir("Salieron " + str(num1) + " y " + str(num2) + ".", "La suma es " + str(suma) + " (" + resultado + ").", "",
              OJ_FRENTE, BO_NEUTRAL)
        time.sleep(0.6)

        ES_banner_fila = 23
        antes = int(reg.creditos)
        if OP_elegida == resultado:
            registrarResultado(pos, PAR_IMPAR, True, apuesta)
            celebrarResultado(True, "♦ ♦ ♦     G A N A S T E     ♦ ♦ ♦")
            decir("¡Ganaste! Sumaste $ " + formatoMiles(apuesta) + ".", "", "", OJ_FRENTE, BO_SORPRESA)
        else:
            registrarResultado(pos, PAR_IMPAR, False, -apuesta)
            celebrarResultado(False, "♦ ♦ ♦     P E R D I S T E     ♦ ♦ ♦")
            decir("Perdiste $ " + formatoMiles(apuesta) + ".", "", "", OJ_GUINO, BO_PICARO)

        reg = leerJugador(pos)
        animarCredito(nombre, antes, int(reg.creditos))
        if reg.creditos < 1:
            hablar(nombre + ", te quedaste en cero. No vas a poder volver a jugar.", OJ_FRENTE, BO_SERIO)


# =============================================================================
# OPCIÓN E: REPORTE (EL LIBRO DE LA CASA)
# =============================================================================

#i, fila, color, largo, pos: int - texto: string

def dibujarReporte():
    if REP_modo == 1:
        pegarTexto(FILA_CONTENIDO, 6, "  #    JUGADOR", colorANSI(C_ORO_CLARO, MESA_pano))
        pegarTexto(FILA_CONTENIDO, 46, "CRÉDITOS", colorANSI(C_ORO_CLARO, MESA_pano))
        for i in range(REP_cant):
            fila = FILA_CONTENIDO + 1 + i
            pos = REP_pos[i]
            if pos == 1:
                color = C_ORO_CLARO
            elif pos == 2:
                color = C_GRIS
            elif pos == 3:
                color = 173
            else:
                color = C_GRIS_OSCURO
            if pos <= 3:
                pegarTexto(fila, 6, "●", colorANSI(color, MESA_pano))
            pegarTexto(fila, 8, str(pos), colorANSI(color, MESA_pano))
            pegarTexto(fila, 13, REP_nom[i][:28], colorANSI(C_BLANCO, MESA_pano))
            texto = "$ " + formatoMiles(int(REP_cred[i]))
            pegarTexto(fila, 54 - len(texto), texto, colorANSI(C_BLANCO, MESA_pano))
            largo = 0
            if REP_maximo > 0:
                largo = 36 * int(REP_cred[i]) // REP_maximo
            if pos > 3:
                color = 34
            pegarTexto(fila, 57, "█" * largo, colorANSI(color, MESA_pano))
    elif REP_modo == 2:
        pegarTexto(FILA_CONTENIDO, 6, "FICHA DE " + REP_nombre, colorANSI(C_ORO_CLARO, MESA_pano))
        pegarTexto(15, 8, "JUEGO", colorANSI(C_ORO, MESA_pano))
        pegarTexto(15, 30, "GANADAS", colorANSI(C_ORO, MESA_pano))
        pegarTexto(15, 62, "PERDIDAS", colorANSI(C_ORO, MESA_pano))
        for i in range(REP_jcant):
            fila = 17 + i * 2
            pegarTexto(fila, 8, REP_jnom[i], colorANSI(C_BLANCO, MESA_pano))
            pegarTexto(fila, 30, str(REP_jg[i]), colorANSI(C_BLANCO, MESA_pano))
            largo = REP_jg[i]
            if largo > 24:
                largo = 24
            pegarTexto(fila, 35, "█" * largo, colorANSI(C_VERDE, MESA_pano))
            pegarTexto(fila, 62, str(REP_jp[i]), colorANSI(C_BLANCO, MESA_pano))
            largo = REP_jp[i]
            if largo > 24:
                largo = 24
            pegarTexto(fila, 67, "█" * largo, colorANSI(C_ROJO_VIVO, MESA_pano))
        if REP_jcant == 0:
            pegarTexto(17, 8, "Este jugador todavía no jugó a ningún juego.", colorANSI(C_GRIS, MESA_pano))
        pegarTexto(24, 8, "Créditos que le quedan: $ " + formatoMiles(int(REP_creditos)), colorANSI(C_ORO_CLARO, MESA_pano))


# Agrega un jugador al ranking. Si la pagina (11 renglones) se llena, la muestra y espera ENTER.
#posicion: int - nombre: string - creditos: float

def agregarAlRanking(posicion, nombre, creditos):
    global REP_cant
    if REP_cant == 11:
        mostrarEnMesa()
        esperarEnter("SIGUIENTE PÁGINA")
        REP_cant = 0
    REP_pos[REP_cant] = posicion
    REP_nom[REP_cant] = nombre
    REP_cred[REP_cant] = creditos
    REP_cant = REP_cant + 1


# Ordena jugadores.dat de mayor a menor credito directamente sobre el archivo
# (intercambiando registros con seek/load/dump, sin arreglos).
# Funciona porque todos los registros ocupan lo mismo (ajustarTexto en el nombre).
#i, j, tam_reg, tam_arch, cant_reg: int
#archivo_jugadores: archivo - aux_i, aux_j: Jugador

def ordenarArchivoJugadores():
    tam_arch = os.path.getsize(RUTA_JUGADORES)
    archivo_jugadores = open(RUTA_JUGADORES, "r+b")

    archivo_jugadores.seek(0, 0)
    aux_i = pickle.load(archivo_jugadores)
    tam_reg = archivo_jugadores.tell()
    cant_reg = tam_arch // tam_reg

    for i in range(0, cant_reg - 1):
        for j in range(i + 1, cant_reg):
            archivo_jugadores.seek(i * tam_reg, 0)
            aux_i = pickle.load(archivo_jugadores)
            archivo_jugadores.seek(j * tam_reg, 0)
            aux_j = pickle.load(archivo_jugadores)

            if aux_i.creditos < aux_j.creditos:
                archivo_jugadores.seek(i * tam_reg, 0)
                pickle.dump(aux_j, archivo_jugadores)
                archivo_jugadores.seek(j * tam_reg, 0)
                pickle.dump(aux_i, archivo_jugadores)
                archivo_jugadores.flush()

    archivo_jugadores.close()


# Opcion A del reporte: ordena el archivo y despues lo recorre mostrando cada jugador.
#tam_arch, posicion: int
#archivo_jugadores: archivo - registro_jugador: Jugador

def reporteJugadoresPorCreditos():
    global REP_modo, REP_cant, REP_maximo
    tam_arch = os.path.getsize(RUTA_JUGADORES)

    if tam_arch == 0:
        hablar("Todavía no hay jugadores registrados.", OJ_FRENTE, BO_SERIO)
    else:
        ordenarArchivoJugadores()

        REP_modo = 1
        REP_cant = 0
        REP_maximo = 0
        archivo_jugadores = open(RUTA_JUGADORES, "rb")
        archivo_jugadores.seek(0, 0)
        posicion = 1
        while archivo_jugadores.tell() < tam_arch:
            registro_jugador = pickle.load(archivo_jugadores)
            if posicion == 1:
                REP_maximo = int(registro_jugador.creditos)
            agregarAlRanking(posicion, registro_jugador.nombre.strip(), registro_jugador.creditos)
            posicion = posicion + 1
        archivo_jugadores.close()
        mostrarEnMesa()
        decir("Jugadores ordenados por créditos,", "de mayor a menor. El que más tiene, arriba.", "", OJ_FRENTE, BO_SONRISA)

# Opcion B del reporte: muestra a que juegos jugo un jugador, cuantas veces
# gano y perdio en cada uno, y cuantos creditos le quedan.
#nombre_jugador: string - nombres_juegos: array de string
#numero_juego, cantidad_ganadas, cantidad_perdidas: int
#jugo_algun_juego: boolean - registro_jugador: Jugador

def reporteJuegosDeUnJugador():
    global REP_modo, REP_nombre, REP_creditos, REP_jcant
    REP_modo = 0
    decir("Decime el nombre y te muestro su ficha.", "", "", OJ_FRENTE, BO_NEUTRAL)
    nombre_jugador = pedirEnMesa("Ingrese el nombre del jugador: ").strip()
    buscarJugador(nombre_jugador)

    if BU_encontrado == False:
        hablar("El jugador " + nombre_jugador + " no está registrado.", OJ_FRENTE, BO_SERIO)
    else:
        registro_jugador = leerJugador(BU_pos)
        nombres_juegos = ["Menor-Mayor", "Numero secreto", "Blackjack", "Par o impar"]
        jugo_algun_juego = False

        REP_nombre = nombre_jugador
        REP_jcant = 0
        for numero_juego in range(4):
            cantidad_ganadas = registro_jugador.juegos[GANADAS][numero_juego]
            cantidad_perdidas = registro_jugador.juegos[PERDIDAS][numero_juego]
            if cantidad_ganadas + cantidad_perdidas > 0:
                jugo_algun_juego = True
                REP_jnom[REP_jcant] = nombres_juegos[numero_juego]
                REP_jg[REP_jcant] = cantidad_ganadas
                REP_jp[REP_jcant] = cantidad_perdidas
                REP_jcant = REP_jcant + 1

        REP_creditos = registro_jugador.creditos
        REP_modo = 2
        mostrarEnMesa()
        if jugo_algun_juego == False:
            decir("Este jugador todavía no jugó a ningún juego.", "", "", OJ_FRENTE, BO_NEUTRAL)
        else:
            decir("Acá está la ficha de " + nombre_jugador[:30] + ".", "", "", OJ_FRENTE, BO_SONRISA)

#opcion: string

def mostrarReporte():
    global REP_modo
    opcion = ""

    while opcion != "C":
        REP_modo = 0
        abrirMesa(PANT_REP, "♦  E L   L I B R O   D E   L A   C A S A  ♦")
        ponerInfo("Reporte de jugadores y partidas")
        ponerMenu("-------- REPORTE --------")
        agregarOpcionMenu("A", "Jugadores por créditos", "De mayor a menor", C_ORO_OSCURO)
        agregarOpcionMenu("B", "Juegos de un jugador", "Ganadas y perdidas", C_MADERA_CLARA)
        agregarOpcionMenu("C", "Volver al menú principal", "Volver al lobby", C_DORSO)
        mostrarEnMesa()
        decir("Este es el libro de la casa.", "Acá queda registrada cada partida.", "¿Qué querés ver?", OJ_FRENTE, BO_NEUTRAL)

        opcion = leerTecla()

        while len(opcion) != 1 or opcion < "A" or opcion > "C":
            avisar("Ingreso Inválido - reintente")
            opcion = leerTecla()

        limpiarAviso()
        elegirOpcionMenu(opcion)
        quitarMenu()
        mostrarEnMesa()

        match opcion:
            case "A":
                reporteJugadoresPorCreditos()
                esperarEnter("VOLVER AL REPORTE")

            case "B":
                reporteJuegosDeUnJugador()
                esperarEnter("VOLVER AL REPORTE")


# =============================================================================
# MÓDULO F: ADMINISTRACIÓN DE JUEGOS (ABM DE CATEGORÍAS Y OPCIONES)
# =============================================================================

# Lee la clave sin mostrarla: en la caja solo aparecen asteriscos
#mensaje, clave, tecla: string - col: int

def leerClaveOculta(mensaje):
    global ES_pregunta
    ES_pregunta = mensaje
    mostrarEnMesa()
    col = 7 + len(mensaje)
    clave = ""
    tecla = ""
    while tecla != "\r":
        tecla = msvcrt.getwch()
        if tecla == "\r":
            ES_pregunta = ""
        elif tecla == "\b":
            if len(clave) > 0:
                clave = clave[:-1]
                ponerCelda(FILA_ENTRADA, col + len(clave), " ", colorANSI(C_BLANCO, C_CAJA))
                volcarFilas(FILA_ENTRADA, FILA_ENTRADA)
        elif tecla == "\x00" or tecla == "\xe0":
            msvcrt.getwch()
        else:
            ponerCelda(FILA_ENTRADA, col + len(clave), "*", colorANSI(C_ORO_CLARO, C_CAJA))
            clave = clave + tecla
            volcarFilas(FILA_ENTRADA, FILA_ENTRADA)
    return clave

#intentos: int - clave_correcta: boolean - ingreso: string

def verificarPasswordAdmin():
    """Valida la contraseña de administrador contra CLAVE_ADMIN (máximo 3 intentos)."""
    intentos = 0
    clave_correcta = False
    while intentos < 3 and clave_correcta == False:
        ponerInfo("Intentos disponibles: " + "● " * (3 - intentos))
        ingreso = leerClaveOculta("Ingrese la contraseña de administrador: ")
        suspenso("Verificando")
        if ingreso == CLAVE_ADMIN:
            clave_correcta = True
        else:
            intentos = intentos + 1
            if intentos < 3:
                ponerInfo("Intentos disponibles: " + "● " * (3 - intentos))
                decir("Contraseña incorrecta.", "Intentos restantes: " + str(3 - intentos), "", OJ_FRENTE, BO_SERIO)
            else:
                ponerInfo("Acceso bloqueado")
                celebrar("♦ ♦ ♦     A C C E S O   D E N E G A D O     ♦ ♦ ♦", C_BLANCO, C_DORSO, 52)
                decir("Superó los 3 intentos de ingresar contraseña,", "salga e intente nuevamente.", "", OJ_FRENTE, BO_SERIO)
    return clave_correcta


def existeCategoriaPorNombre(nombre_buscado):
    """Comprueba si ya existe una categoría con el mismo nombre (insensible a mayúsculas)."""
    encontrado = False
    if os.path.exists(RUTA_CATEGORIAS):
        tam = os.path.getsize(RUTA_CATEGORIAS)
        archivo = open(RUTA_CATEGORIAS, "rb")
        while archivo.tell() < tam and encontrado == False:
            reg = pickle.load(archivo)
            if reg.nombre.strip().upper() == nombre_buscado.strip().upper():
                encontrado = True
        archivo.close()
    return encontrado


def obtenerUltimoNroCategoria():
    """Retorna el último NroCategoria registrado para autoincrementar desde 1."""
    ultimo = 0
    if os.path.exists(RUTA_CATEGORIAS):
        tam = os.path.getsize(RUTA_CATEGORIAS)
        archivo = open(RUTA_CATEGORIAS, "rb")
        while archivo.tell() < tam:
            reg = pickle.load(archivo)
            ultimo = reg.nro_categoria
        archivo.close()
    return ultimo


def esCategoriaActiva(nro_cat):
    """Verifica si una categoría existe y su estado es 'A' (Activa)."""
    es_activa = False
    if os.path.exists(RUTA_CATEGORIAS):
        tam = os.path.getsize(RUTA_CATEGORIAS)
        archivo = open(RUTA_CATEGORIAS, "rb")
        while archivo.tell() < tam and es_activa == False:
            reg = pickle.load(archivo)
            if reg.nro_categoria == nro_cat and reg.estado == "A":
                es_activa = True
        archivo.close()
    return es_activa


def mostrarCategoriasActivas():
    """Muestra en el paño todas las categorías con estado 'A' y retorna la cantidad."""
    cant = 0
    if os.path.exists(RUTA_CATEGORIAS):
        tam = os.path.getsize(RUTA_CATEGORIAS)
        archivo = open(RUTA_CATEGORIAS, "rb")
        quitarMenu()
        empezarLista("--- CATEGORÍAS ACTIVAS ---")
        while archivo.tell() < tam:
            reg = pickle.load(archivo)
            if reg.estado == "A":
                agregarALista(f"N° {reg.nro_categoria} - {limpiarTexto(reg.nombre)}")
                cant = cant + 1
        archivo.close()
        mostrarEnMesa()
    return cant


def obtenerUltimoNroOpcion(nro_cat):
    """Retorna el último número secuencial de opción para una categoría específica."""
    ultimo = 0
    if os.path.exists(RUTA_OPCIONES):
        tam = os.path.getsize(RUTA_OPCIONES)
        archivo = open(RUTA_OPCIONES, "rb")
        while archivo.tell() < tam:
            reg = pickle.load(archivo)
            if reg.nro_categoria == nro_cat:
                ultimo = reg.nro_opcion
        archivo.close()
    return ultimo


# -----------------------------------------------------------------------------
# ABM DE CATEGORÍAS
# -----------------------------------------------------------------------------
#texto: string - fin: int

def limpiarTexto(texto):
    fin = len(texto)
    while fin > 0 and texto[fin - 1] == " ":
        fin = fin - 1
    return texto[:fin]


#mensaje, texto: string - largo: int

def pedirTexto(mensaje, largo):
    texto = pedirEnMesa(mensaje)
    while limpiarTexto(texto) == "" or len(texto.encode("utf-8")) > largo:
        if limpiarTexto(texto) == "":
            avisar("Error: este dato no puede quedar vacio.")
        else:
            avisar(f"Error: el texto es demasiado largo (maximo {largo} caracteres).")
        texto = pedirEnMesa(mensaje)
    limpiarAviso()
    return texto


# Titulo del formulario en el paño
#titulo: string

def ponerFormulario(titulo):
    quitarMenu()
    empezarLista(titulo)
    mostrarEnMesa()


#nombre, pregunta: string - reg: Categoria - archivo: archivo

def altaCategoria():
    ponerFormulario("--- ALTA DE CATEGORÍA ---")
    decir("Vamos a crear una categoría nueva.", "Primero, el nombre.", "", OJ_FRENTE, BO_NEUTRAL)
    nombre = pedirTexto("Ingrese el nombre de la categoría: ", 30)
    if existeCategoriaPorNombre(nombre) == True:
        hablar(f"Error: Ya existe una categoría llamada '{nombre}'.", OJ_FRENTE, BO_SERIO)
    else:
        decir("Perfecto. Ahora la pregunta del juego.", "", "", OJ_FRENTE, BO_NEUTRAL)
        pregunta = pedirTexto("Ingrese la pregunta (ej. ¿Quién es más alto?): ", 200)
        reg = Categoria()
        reg.nro_categoria = obtenerUltimoNroCategoria() + 1
        reg.nombre = ajustarTexto(nombre, 30)
        reg.pregunta = ajustarTexto(pregunta, 200)
        reg.estado = "A"

        archivo = open(RUTA_CATEGORIAS, "ab")
        pickle.dump(reg, archivo)
        archivo.close()

        decir(f"¡Categoría N° {reg.nro_categoria} registrada con éxito!", "", "", OJ_FRENTE, BO_SONRISA)


#cant_activas, nro, tam, pos_inicio: int - nuevo_nombre: string - modificado: boolean

def modificacionCategoria():
    cant_activas = mostrarCategoriasActivas()
    if cant_activas == 0:
        hablar("No hay categorías activas para modificar.", OJ_FRENTE, BO_SERIO)
    else:
        decir("¿Qué categoría querés modificar?", "", "", OJ_FRENTE, BO_NEUTRAL)
        validarNumero("Ingrese el N° de categoría a modificar: ", 1, obtenerUltimoNroCategoria())
        nro = NU_numero
        if esCategoriaActiva(nro) == False:
            hablar("Error: El número ingresado no corresponde a una categoría activa.", OJ_FRENTE, BO_SERIO)
        else:
            nuevo_nombre = pedirTexto("Ingrese el nuevo nombre para la categoría: ", 30)
            if existeCategoriaPorNombre(nuevo_nombre) == True:
                hablar(f"Error: Ya existe una categoría llamada '{nuevo_nombre}'. No se modificó nada.", OJ_FRENTE, BO_SERIO)
            else:
                tam = os.path.getsize(RUTA_CATEGORIAS)
                archivo = open(RUTA_CATEGORIAS, "r+b")
                modificado = False
                while archivo.tell() < tam and modificado == False:
                    pos_inicio = archivo.tell()
                    reg = pickle.load(archivo)
                    if reg.nro_categoria == nro and reg.estado == "A":
                        reg.nombre = ajustarTexto(nuevo_nombre, 30)
                        archivo.seek(pos_inicio)
                        pickle.dump(reg, archivo)
                        modificado = True
                archivo.close()
                decir("¡Nombre de categoría actualizado correctamente!", "", "", OJ_FRENTE, BO_SONRISA)


#cant_activas, nro, tam, pos_inicio: int - procesado: boolean

def bajaCategoria():
    cant_activas = mostrarCategoriasActivas()
    if cant_activas == 0:
        hablar("No hay categorías activas para dar de baja.", OJ_FRENTE, BO_SERIO)
    else:
        decir("¿Qué categoría damos de baja?", "", "", OJ_FRENTE, BO_SERIO)
        validarNumero("Ingrese el N° de categoría a dar de baja: ", 1, obtenerUltimoNroCategoria())
        nro = NU_numero
        if esCategoriaActiva(nro) == False:
            hablar("Error: El número ingresado no corresponde a una categoría activa.", OJ_FRENTE, BO_SERIO)
        else:
            tam = os.path.getsize(RUTA_CATEGORIAS)
            archivo = open(RUTA_CATEGORIAS, "r+b")
            procesado = False
            while archivo.tell() < tam and procesado == False:
                pos_inicio = archivo.tell()
                reg = pickle.load(archivo)
                if reg.nro_categoria == nro and reg.estado == "A":
                    reg.estado = "I"  # Baja lógica
                    archivo.seek(pos_inicio)
                    pickle.dump(reg, archivo)
                    procesado = True
            archivo.close()
            hablar(f"¡Categoría N° {nro} dada de baja (Inactiva) exitosamente!", OJ_FRENTE, BO_NEUTRAL)


# -----------------------------------------------------------------------------
# ABM DE OPCIONES
# -----------------------------------------------------------------------------

#cant_activas, nro_cat, valor: int - objeto: string - reg_op: Opcion

def altaOpcion():
    cant_activas = mostrarCategoriasActivas()
    if cant_activas == 0:
        hablar("Antes de registrar opciones se deben dar de alta categorías.", OJ_FRENTE, BO_SERIO)
    else:
        decir("¿A qué categoría le agregamos una opción?", "", "", OJ_FRENTE, BO_NEUTRAL)
        validarNumero("Ingrese el N° de la categoría para asociar la opción: ", 1, obtenerUltimoNroCategoria())
        nro_cat = NU_numero
        if esCategoriaActiva(nro_cat) == False:
            hablar("Error: La categoría no existe o no está activa.", OJ_FRENTE, BO_SERIO)
        else:
            ponerFormulario("--- NUEVA OPCIÓN PARA LA CATEGORÍA N° " + str(nro_cat) + " ---")
            decir("Ahora el objeto y su valor numérico.", "Ej: Objeto: Tom Cruise - Valor: 61", "", OJ_FRENTE, BO_NEUTRAL)
            objeto = pedirTexto("Ingrese el Objeto / Elemento: ", 100)
            validarNumero("Ingrese el Valor numérico de comparación: ", 0, 2000000000)
            valor = NU_numero

            reg_op = Opcion()
            reg_op.nro_categoria = nro_cat
            reg_op.nro_opcion = obtenerUltimoNroOpcion(nro_cat) + 1
            reg_op.objeto = ajustarTexto(objeto, 100)
            reg_op.valor = valor

            archivo = open(RUTA_OPCIONES, "ab")
            pickle.dump(reg_op, archivo)
            archivo.close()

            hablar(f"¡Opción '{objeto}' (Valor: {valor}) registrada en la Categoría N° {nro_cat}!", OJ_FRENTE, BO_SONRISA)


#cant_activas, nro_cat, tam_cat, tam_op, cant_ops: int - pregunta: string

def consultaOpciones():
    cant_activas = mostrarCategoriasActivas()
    if cant_activas == 0:
        hablar("No hay categorías activas registradas.", OJ_FRENTE, BO_SERIO)
    else:
        decir("¿Qué categoría querés consultar?", "", "", OJ_FRENTE, BO_NEUTRAL)
        validarNumero("Ingrese el N° de categoría a consultar: ", 1, obtenerUltimoNroCategoria())
        nro_cat = NU_numero
        if esCategoriaActiva(nro_cat) == False:
            hablar("Error: La categoría no existe o no está activa.", OJ_FRENTE, BO_SERIO)
        else:
            pregunta = ""
            tam_cat = os.path.getsize(RUTA_CATEGORIAS)
            arch_cat = open(RUTA_CATEGORIAS, "rb")
            while arch_cat.tell() < tam_cat and pregunta == "":
                reg_c = pickle.load(arch_cat)
                if reg_c.nro_categoria == nro_cat:
                    pregunta = reg_c.pregunta.strip()
            arch_cat.close()

            hablar(f"Pregunta: {pregunta}", OJ_FRENTE, BO_NEUTRAL)
            empezarLista("--- OBJETOS Y VALORES CARGADOS ---")

            cant_ops = 0
            if os.path.exists(RUTA_OPCIONES):
                tam_op = os.path.getsize(RUTA_OPCIONES)
                arch_op = open(RUTA_OPCIONES, "rb")
                while arch_op.tell() < tam_op:
                    reg_o = pickle.load(arch_op)
                    if reg_o.nro_categoria == nro_cat:
                        agregarALista(f"{limpiarTexto(reg_o.objeto)[:28]} -> Valor: {reg_o.valor}")
                        cant_ops = cant_ops + 1
                arch_op.close()

            if cant_ops == 0:
                agregarALista("(Aún no hay opciones registradas para esta categoría)")
            mostrarEnMesa()
            esperarEnter("VOLVER")


# -----------------------------------------------------------------------------
# MENÚS ITERATIVOS DEL MÓDULO F
# -----------------------------------------------------------------------------

#opc: int

def menuAdministrarCategorias():
    opc = 0
    while opc != 4:
        ponerMenu("--- ADMINISTRAR CATEGORÍAS ---")
        agregarOpcionMenu("1", "Alta", "Nueva categoría", C_VERDE)
        agregarOpcionMenu("2", "Modificación", "Cambiar el nombre", 33)
        agregarOpcionMenu("3", "Baja", "Pasarla a inactiva", C_ROJO_CARTA)
        agregarOpcionMenu("4", "Volver", "Menú anterior", C_GRIS_OSCURO)
        validarNumero("Seleccione una opción: ", 1, 4)
        opc = NU_numero
        elegirOpcionMenu(str(opc))
        quitarMenu()
        mostrarEnMesa()

        match opc:
            case 1:
                altaCategoria()
            case 2:
                modificacionCategoria()
            case 3:
                bajaCategoria()
            case 4:
                decir("Volviendo...", "", "", OJ_FRENTE, BO_NEUTRAL)

#opc: int

def menuAdministrarOpciones():
    opc = 0
    while opc != 3:
        ponerMenu("--- ADMINISTRAR OPCIONES ---")
        agregarOpcionMenu("1", "Alta", "Nueva opción", C_VERDE)
        agregarOpcionMenu("2", "Consulta", "Ver objetos y valores", 33)
        agregarOpcionMenu("3", "Volver", "Menú anterior", C_GRIS_OSCURO)
        validarNumero("Seleccione una opción: ", 1, 3)
        opc = NU_numero
        elegirOpcionMenu(str(opc))
        quitarMenu()
        mostrarEnMesa()

        match opc:
            case 1:
                altaOpcion()
            case 2:
                consultaOpciones()
            case 3:
                decir("Volviendo...", "", "", OJ_FRENTE, BO_NEUTRAL)


#opc: int

def moduloAdministracion():
    abrirMesa(PANT_ADMIN, "♦  O F I C I N A   D E   G E R E N C I A  ♦")
    decir("Esta es la oficina de la gerencia.", "Para pasar necesito la contraseña de administrador.", "",
          OJ_FRENTE, BO_SERIO)
    if verificarPasswordAdmin() == True:
        ponerInfo("Acceso concedido · Administrador")
        celebrar("♦ ♦ ♦     A C C E S O   C O N C E D I D O     ♦ ♦ ♦", C_NEGRO, C_VERDE, 22)
        decir("Acceso concedido. Adelante.", "", "", OJ_FRENTE, BO_SONRISA)
        quitarCartel()
        opc = 0
        while opc != 3:
            ponerMenu("F. ADMINISTRACIÓN DE JUEGOS (ABM)")
            agregarOpcionMenu("1", "Administrar Categorías", "Alta, modificación y baja", C_ORO_OSCURO)
            agregarOpcionMenu("2", "Administrar Opciones", "Alta y consulta", 33)
            agregarOpcionMenu("3", "Volver al Menú Principal", "Volver al lobby", C_DORSO)
            validarNumero("Seleccione una opción: ", 1, 3)
            opc = NU_numero
            elegirOpcionMenu(str(opc))

            match opc:
                case 1:
                    menuAdministrarCategorias()
                case 2:
                    menuAdministrarOpciones()
                case 3:
                    quitarMenu()
                    mostrarEnMesa()
                    decir("Volviendo al menú principal...", "", "", OJ_FRENTE, BO_NEUTRAL)


# =============================================================================
# PROGRAMA PRINCIPAL: EL LOBBY DEL CASINO
# =============================================================================

def armarMenuPrincipal():
    ponerMenu("")
    agregarOpcionMenu("A", "JUEGO DEL MENOR-MAYOR", "¿Cuál vale más? Seis rondas", 26)
    agregarOpcionMenu("B", "ADIVINAR EL NÚMERO SECRETO", "Abrí la bóveda en 5 intentos", 30)
    agregarOpcionMenu("C", "BLACKJACK", "Llegá a 21 sin pasarte", 28)
    agregarOpcionMenu("D", "PAR O IMPAR", "Dos dados, una apuesta", C_ROJO_CARTA)
    agregarOpcionMenu("E", "REPORTE", "El libro de la casa", C_ORO_OSCURO)
    agregarOpcionMenu("F", "ADMINISTRACIÓN DE JUEGOS", "Solo gerencia", C_GRIS_OSCURO)
    agregarOpcionMenu("G", "SALIR", "Cerrar el casino", C_DORSO)


#opc: string - primera: boolean

def main():
    prepararConsola()
    cartel_inicio()
    opc = ""
    primera = True

    while opc != "G":
        abrirMesa(PANT_MENU, "♦  C A S I N O   U T N   ·   L O B B Y  ♦")
        ponerInfo("Esta noche: 4 mesas de juego abiertas")
        armarMenuPrincipal()
        mostrarEnMesa()
        if primera == True:
            decir("Bienvenido al Casino UTN.", "Cuatro mesas, el libro de la casa y la gerencia.",
                  "Presioná la letra de la mesa a la que querés ir.", OJ_FRENTE, BO_SONRISA)
            primera = False
        else:
            decir("¿A qué mesa vamos ahora?", "Presioná la letra de la opción.", "", OJ_FRENTE, BO_SONRISA)

        opc = leerTecla()

        while (len(opc) != 1 or opc < "A" or opc > "G"):
            avisar("Ingreso Inválido - reintente")
            opc = leerTecla()

        limpiarAviso()
        elegirOpcionMenu(opc)

        match opc:
            case "A":
                EjecutarJuegoMenorMayor()
                esperarEnter("VOLVER AL MENÚ PRINCIPAL")

            case "B":
                nro_secreto()
                esperarEnter("VOLVER AL MENÚ PRINCIPAL")

            case "C":
                blackjack()
                esperarEnter("VOLVER AL MENÚ PRINCIPAL")

            case "D":
                par_impar()
                esperarEnter("VOLVER AL MENÚ PRINCIPAL")

            case "E":
                mostrarReporte()
                esperarEnter("VOLVER AL MENÚ PRINCIPAL")

            case "F":
                moduloAdministracion()
                esperarEnter("VOLVER AL MENÚ PRINCIPAL")

            case "G":
                cartel_despedida_animado()

main()
