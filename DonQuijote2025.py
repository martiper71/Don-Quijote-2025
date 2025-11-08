import tkinter as tk
import os

# ---------------------------
# 1. DATOS DEL JUEGO
# ---------------------------

# Descripción base fija de cada sala (sin objetos dinámicos).
# El índice de la lista coincide con el número de habitación que utiliza el motor.
txt_base = [
    "",
# Habitación 1
    "Los libros polvorientos destacan en una estantería situada hacia la izquierda. "
    "Una puerta abre el camino hacia el sur.",

# Habitación 2
    "Tu habitación es austera como corresponde a un hidalgo manchego del siglo XVI. "
    "Una escalera conecta tu habitación con el piso inferior. "
    "También puedes ir al norte.",

# Habitación 3
    "Estás en el zaguán. Una amplia escalera te facilitará el acceso al piso superior. "
    "Puedes subir, ir al norte, sur y este.",

# Habitación 4
    "En la antigua y acogedora cocina desnuda de todo lo que pueda recordar olorosas "
    "comidas queda una triste alacena. Hay una puerta hacia el sur y otra hacía el "
    "norte.",

# Habitación 5
    "La tenue luz que penetra por la puerta permite vislumbrar un baul, cuya superficie "
    "cubierta por el polvo de los siglos encubre recuerdos de tus antepasados. Puedes "
    "ir al sur.",

# Habitación 6
    "Te encuentras en el comedor de tu casa. Rústico y sencillo gobernado por una "
    "mesa de madera. Algo cuelga de la pared. Una puerta conduce al norte.",

# Habitación 7
    "El portalón de tu casa, iluminado por la luz de un candelabro, te abrirá las "
    "puertas de tu nueva vida. El portalón está hacia el este, hay otro hacía el "
    "oeste.",

# Habitación 8
    "Argamasilla de Alba, tu pueblo. Sus solitarias calles y piedras están mudas ante "
    "ti. ¿Qué dirá este bando que hay en un muro? Hay una calle hacia el oeste y otra "
    "hacia el sur."   

# Habitación 9
]

img = [
    "imagenes/000.png",
    "imagenes/001.png",
    "imagenes/002.png",
    "imagenes/003.png",
    "imagenes/004.png",
    "imagenes/005.png",
    "imagenes/006.png",
    "imagenes/007.png",
    "imagenes/008.png",
]

# Vector de banderas de estado globales.
# cond[1] controla si puedes ir al sur desde la habitación 1
# cond[2] indica si llevas la armadura puesta
# cond[3] controla si ya has descubierto la armadura en el baúl (hab 5)
# cond[4] indica si la alacena (hab 4) está abierta
# cond[5] indica si la llave de la alacena ya ha sido descubierta mediante 'examinar alacena'
cond = ["", 
        "n",
        "n",
        "n",
        "n",
        "n"
]

# Objetos iniciales en cada sala.
# El motor extrae los objetos de este diccionario y lo va
# actualizando cuando el jugador coge o deja algo.
OBJETOS_INICIALES = {
    1: ["libro"],
    2: [],
    3: [],
    4: ["llave"],
    5: ["armadura"],
    6: ["pan", "espada"],
}

DESCRIPCIONES_OBJETOS = {
    "libro": {
        "sala": "Se trata de un libro de caballerías repleto de hazañas.",
        "inventario": "Es tu preciado libro de caballerías.",
    },
    "armadura": {
        "sala": "Una armadura con señales del paso del tiempo, pero aún resistente.",
        "inventario": "Notas el peso de la armadura; te hará invulnerable a pequeños ataques.",
    },
    "llave": {
        "sala": "Una llave de hierro forjado cuelga discretamente.",
        "inventario": "Guardas la llave con cuidado, podría abrir un portal importante.",
    },
    "espada": {
        "sala": "Una espada algo mellada, aunque todavía capaz de luchar.",
        "inventario": "Sientes la espada cerca, lista para blandirse si hace falta.",
    },
    "pan": {
        "sala": "Ves un currusco de pan, duro pero comestible.",
        "inventario": "El currusco de pan podría aliviar el hambre durante el viaje.",
    },
    "camisa": {
        "sala": "Una camisa sencilla de lino se mantiene doblada con esmero.",
        "inventario": "Tu camisa habitual, sencilla y cómoda.",
    },
}

def clonar_objetos_iniciales():
    """Devuelve una copia profunda simple del estado inicial de objetos."""
    return {hab: list(objetos) for hab, objetos in OBJETOS_INICIALES.items()}

def restablecer_estado_inicial():
    """
    Restituye inventario, posición y banderas como si la partida empezara de cero.
    """
    global habitacion_actual, cond, inventario, objetos_en_sala

    habitacion_actual = 1  # dormitorio
    cond = ["", "n", "n", "n", "n", "n"]
    inventario = ["camisa"]
    objetos_en_sala = clonar_objetos_iniciales()

# Inicializamos los valores por primera vez.
restablecer_estado_inicial()

def objetos_visibles_en_sala(hab):
    """
    Devuelve la lista de objetos visibles en una sala determinada,
    aplicando lógicas de aparición condicional.
    """
    visibles = list(objetos_en_sala.get(hab, []))

    if hab == 5 and cond[3] != "s" and "armadura" in visibles:
        visibles.remove("armadura")
    
    # La llave de la habitación 4 sólo es visible si ya la has descubierto
    # (es decir, si has examinado la alacena con la alacena abierta).
    if hab == 4 and "llave" in visibles and cond[5] != "s":
        visibles.remove("llave")

    return visibles


# Estado global que indica si el jugador está muerto esperando reinicio.
estado_muerte = False

# ---------------------------
# 2. HELPERS DE TEXTO / OBJETOS
# ---------------------------

def lista_a_texto_natural(lista):
    """
    ["camisa"] -> "camisa"
    ["camisa","pan"] -> "camisa y pan"
    ["camisa","pan","lanza"] -> "camisa, pan y lanza"
    """
    # Formatea listas en castellano, añadiendo "y" en el último elemento.
    if len(lista) == 0:
        return ""
    if len(lista) == 1:
        return lista[0]
    if len(lista) == 2:
        return lista[0] + " y " + lista[1]
    return ", ".join(lista[:-1]) + " y " + lista[-1]


def articulo_objeto(nombre):
    """
    Devuelve el fragmento a mostrar en sala al listar objetos.
    Ejemplo:
      "pan"    -> "un currusco de "
      "camisa" -> "una "
      "libro"  -> "un "
    OJO: esto es solo para la frase "También puedes observar que hay ..."
    """
    articulos = {
        "pan": "un currusco de ",
        "camisa": "una ",
        "libro": "un ",
        "armadura": "una ",
        "llave": "una ",
        "espada": "una "
    }
    # Si no encontramos el objeto, devolvemos un artículo neutro.
    return articulos.get(nombre, "un ")


def nombre_visible_inventario(nombre):
    """
    Cómo se nombra el objeto al hablar de él de forma humana.
    Esto es lo que sale en inventario, al coger/dejar, al mirar algo concreto, etc.
    """
    visibles = {
        "pan": "un currusco de pan",
        "camisa": "una camisa",
        "libro": "un libro",
        "armadura": "una armadura",
        "llave": "una llave",
        "espada": "una espada",
    }
    # Si el objeto no está en la tabla, devolvemos su nombre literal.
    return visibles.get(nombre, nombre)


def normaliza_objeto_usuario(texto_objeto):
    """
    Recibe lo que ha escrito el jugador: 'pan', 'currusco', 'currusco de pan',
    'libro', 'el libro', 'una camisa', etc.
    Devuelve el nombre interno ('pan', 'libro', 'camisa') o None si no lo reconoce.
    """
    if texto_objeto is None:
        return None

    t = texto_objeto.strip().lower()

    # intentar quitar artículo inicial simple
    articulos_iniciales = [
        "el ", "la ", "los ", "las ",
        "un ", "una ", "unos ", "unas ",
        "mi ", "mis "
    ]
    for art in articulos_iniciales:
        if t.startswith(art):
            t = t[len(art):].strip()
            break

    # Mapa de alias → nombre interno
    alias = {
        # pan
        "pan": "pan",
        "currusco": "pan",
        "currusco de pan": "pan",
        "un currusco de pan": "pan",
        "el currusco de pan": "pan",

        # camisa
        "camisa": "camisa",
        "mi camisa": "camisa",
        "una camisa": "camisa",

        # libro
        "libro": "libro",
        "libro de caballerías": "libro",
        "libro de caballerias": "libro",
        "un libro de caballerías": "libro",
        "un libro de caballerias": "libro",
        "el libro": "libro",
    }

    if t in alias:
        return alias[t]

    # fallback por palabras clave
    # Si no coincide con un alias exacto, buscamos palabras clave
    # dentro del texto escrito por el usuario para recuperar el
    # nombre interno canónico del objeto.
    if "currusco" in t or "pan" in t:
        return "pan"
    if "camisa" in t:
        return "camisa"
    if "libro" in t:
        return "libro"
    if "caballer" in t:  # "caballerías"
        return "libro"
    if "armadura" in t:
        return "armadura"
    if "llave" in t:
        return "llave"
    if "espada" in t:
        return "espada"

    return None


def descripcion_objeto(nombre, origen):
    """
    Devuelve una descripción detallada del objeto según dónde esté.
    origen puede ser 'sala' o 'inventario'.
    """
    info = DESCRIPCIONES_OBJETOS.get(nombre, {})

    if isinstance(info, dict):
        if origen == "inventario":
            return info.get("inventario") or info.get("sala") or f"Llevas {nombre_visible_inventario(nombre)} contigo."
        return info.get("sala") or f"Observas {nombre_visible_inventario(nombre)}."

    # Si info es un string simple, úsalo en ambos contextos.
    if origen == "inventario":
        return info or f"Llevas {nombre_visible_inventario(nombre)} contigo."
    return info or f"Observas {nombre_visible_inventario(nombre)}."


def inventario_texto():
    """
    Texto que se ve al hacer INVENTARIO.
    """
    # Construimos una frase legible según el número de objetos que lleves.
    if len(inventario) == 0:
        return "No llevas nada encima."

    visibles = [nombre_visible_inventario(obj) for obj in inventario]

    if len(visibles) == 1:
        return f"Llevas {visibles[0]}."
    else:
        return "Llevas " + lista_a_texto_natural(visibles) + "."


def descripcion_con_objetos(hab):
    """
    Construye la descripción dinámica de la sala combinando:
    - txt_base[hab]
    - 'También puedes observar que hay ...' según objetos_en_sala[hab]
    """
    base = txt_base[hab]

    objs = objetos_visibles_en_sala(hab)

    if len(objs) == 0:
        return base

    # Queremos algo tipo:
    # "También puedes observar que hay un currusco de pan."
    # o "También puedes observar que hay un libro de caballerías."
    #
    # Para múltiples objetos, hacemos una frase simple un poco más genérica.

    if len(objs) == 1:
        o = objs[0]
        # Para el pan queremos "un currusco de pan"
        # Para el libro queremos "un libro de caballerías"
        # Para camisa "una camisa"
        extra_nombre = nombre_visible_inventario(o)
        extra = f" También puedes observar que hay {extra_nombre}."
        return base + " " + extra.strip()

    else:
        # varios objetos
        visibles = [nombre_visible_inventario(o) for o in objs]
        lista = lista_a_texto_natural(visibles)
        extra = f" También puedes observar que hay {lista}."
        return base + " " + extra.strip()


# ---------------------------
# 3. PARSER
# ---------------------------

def normaliza_direccion(palabra):
    """
    'norte','n' → 'n'
    'sur','s' → 's'
    'bajar','abajo' → 'bajar'
    'subir','arriba' → 'subir'
    """
    # Traducimos distintas formas de escribir la misma dirección
    # a un código único que entiende el motor.
    mapa = {
        "n": "n",
        "norte": "n",
        "s": "s",
        "sur": "s",
        "e": "e",
        "este": "e",
        "o": "o",
        "oeste": "o",
        "subir": "subir",
        "arriba": "subir",
        "bajar": "bajar",
        "abajo": "bajar"
    }
    return mapa.get(palabra, None)


def parsear(frase_usuario):
    """
    Convierte el texto que ha escrito el jugador en (verbo, objeto).
    """
    tokens = frase_usuario.strip().lower().split()

    if len(tokens) == 0:
        return None, None

    # Cuando el comando solo tiene una palabra intentamos interpretarla
    # como dirección, acciones básicas (inventario, mirar, fin) o bien
    # como un verbo sin objeto.
    # Ej: "n", "inventario", "mirar", "fin"
    if len(tokens) == 1:
        palabra = tokens[0]

        # ¿dirección?
        dir_norm = normaliza_direccion(palabra)
        if dir_norm is not None:
            return "ir", dir_norm

        # inventario
        if palabra in ["inventario", "inv", "i"]:
            return "inventario", None

        # mirar
        if palabra in ["mirar", "mira", "examinar", "look", "l"]:
            return "mirar", None

        # fin
        if palabra in ["fin", "salir", "quit"]:
            return "fin", None

        # cualquier otra palabra pasa a ser un verbo sin objeto
        return palabra, None

    # 2+ palabras ("coger pan", "mirar currusco de pan")
    # Consideramos la primera palabra como el verbo y el resto como el objeto.
    primera = tokens[0]

    # si la primera palabra es dirección ("sur ahora")
    dir_norm = normaliza_direccion(primera)
    if dir_norm is not None:
        return "ir", dir_norm

    # inventario adornado
    if primera in ["inventario", "inv", "i"]:
        return "inventario", None

    verbo = primera
    objeto = " ".join(tokens[1:])
    return verbo, objeto


# ---------------------------
# 4. MOTOR DEL JUEGO
# ---------------------------

def ejecutar_comando(verbo, objeto):
    """
    Devuelve (nueva_hab, descripcion_sala, mensaje_extra)
    """
    global habitacion_actual, cond, inventario, objetos_en_sala

    hab = habitacion_actual

    # Cada bloque de este motor gestiona un verbo concreto.
    # Siempre devolvemos la habitación final, la descripción que hay que mostrar
    # y un mensaje adicional (si aplica) para la parte inferior de la pantalla.

    def morir_por_rata():
        """
        Maneja la secuencia de muerte por la rata en la alacena.
        Devuelve un mensaje especial que el interfaz tratará aparte.
        """
        global estado_muerte
        estado_muerte = True
        mensaje = "Una rata salta y te muerde. Estas muerto.\nPulsa una tecla ..."
        return habitacion_actual, "", mensaje

    # INVENTARIO
    if verbo == "inventario":
        return habitacion_actual, descripcion_con_objetos(habitacion_actual), inventario_texto()

    # MIRAR / EXAMINAR
    if verbo in ["examinar", "mirar"]:
        if objeto:
            texto_objeto = objeto.strip().lower()

            if hab == 5:
                texto_sin_tildes = (
                    texto_objeto.replace("á", "a")
                    .replace("é", "e")
                    .replace("í", "i")
                    .replace("ó", "o")
                    .replace("ú", "u")
                )
                if "baul" in texto_sin_tildes:
                    cond[3] = "s"
                    mensaje = "Entre las muchas anticuallas destaca una armadura."
                    return habitacion_actual, descripcion_con_objetos(habitacion_actual), mensaje

            # Nuevo: examinar la alacena en la habitación 4
            texto_sin_tildes = (
                texto_objeto.replace("á", "a")
                .replace("é", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
            )
            if hab == 4 and ("alacena" in texto_sin_tildes or "la alacena" in texto_sin_tildes):
                if cond[4] == "s":
                    # alacena ya está abierta -> al examinar aparece la llave
                    cond[5] = "s"  # marca que la llave está descubierta/visible
                    return habitacion_actual, descripcion_con_objetos(habitacion_actual), "Hay una llave."
                else:
                    return habitacion_actual, descripcion_con_objetos(habitacion_actual), "La alacena está cerrada."

            # Caso general existente para mirar objetos...
            nombre_normalizado = normaliza_objeto_usuario(objeto)

            if nombre_normalizado:
                # mirar un objeto que está en la sala
                if nombre_normalizado in objetos_visibles_en_sala(hab):
                    mensaje = descripcion_objeto(nombre_normalizado, "sala")
                    return habitacion_actual, descripcion_con_objetos(habitacion_actual), mensaje

                # mirar algo que llevas encima
                if nombre_normalizado in inventario:
                    mensaje = descripcion_objeto(nombre_normalizado, "inventario")
                    return habitacion_actual, descripcion_con_objetos(habitacion_actual), mensaje

            # nada reconocible
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No ves nada especial."
        else:
            # mirar sin objeto = repetir descripción dinámica
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), None

    # LEER LIBRO
    # Debe desbloquear la salida SUR desde la habitación 1
    if verbo == "leer":
        nombre_normalizado = normaliza_objeto_usuario(objeto)

        # Solo reaccionamos si intenta leer el libro
        if nombre_normalizado == "libro":
            # ¿tienes el libro o está en la sala contigo?
            libro_aqui = (
                ("libro" in inventario) or
                ("libro" in objetos_en_sala.get(hab, []))
            )

            if libro_aqui:
                # Al leerlo se desbloquea la salida sur del dormitorio.
                cond[1] = "s"
                mensaje = (
                    "Empieza la aventura."
                )
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), mensaje
            else:
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), "¿Leer qué? Aquí no ves ese libro."
        # leer otra cosa
        return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No tiene sentido leer eso."

    # PONERSE / EQUIPAR ARMADURA
    if verbo in ["poner", "ponerse", "vestir", "vestirse", "equipar"]:
        if objeto is None or objeto == "":
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "¿Qué quieres ponerte?"

        nombre_normalizado = normaliza_objeto_usuario(objeto)

        if nombre_normalizado != "armadura":
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No parece que puedas ponerte eso."

        if "armadura" not in inventario:
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No llevas esa armadura contigo."

        if cond[2] == "s":
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "Ya llevas puesta la armadura."

        cond[2] = "s"
        return habitacion_actual, descripcion_con_objetos(habitacion_actual), "Te colocas la armadura y te sientes protegido."

    # COGER OBJETO
    if verbo in ["coger", "agarrar", "tomar"]:
        if objeto is None or objeto == "":
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "¿Coger qué?"

        nombre_normalizado = normaliza_objeto_usuario(objeto)

        if nombre_normalizado is None:
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No sé qué quieres coger."

        if nombre_normalizado not in objetos_visibles_en_sala(hab):
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "Eso no está aquí."

        sala_objs = objetos_en_sala.get(hab, [])

        if nombre_normalizado in sala_objs:
            # Transferimos el objeto de la sala al inventario del jugador.
            sala_objs.remove(nombre_normalizado)
            inventario.append(nombre_normalizado)
            mensaje = f"Has cogido {nombre_visible_inventario(nombre_normalizado)}."
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), mensaje
        else:
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "Eso no está aquí."

    # DEJAR OBJETO
    if verbo in ["dejar", "soltar"]:
        if objeto is None or objeto == "":
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "¿Dejar qué?"

        nombre_normalizado = normaliza_objeto_usuario(objeto)

        if nombre_normalizado is None:
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No sé qué quieres dejar."

        if nombre_normalizado in inventario:
            # Quitamos el objeto del inventario y lo dejamos en la sala actual.
            inventario.remove(nombre_normalizado)
            objetos_en_sala.setdefault(hab, []).append(nombre_normalizado)
            if nombre_normalizado == "armadura":
                cond[2] = "n"
            mensaje = f"Has dejado {nombre_visible_inventario(nombre_normalizado)} aquí."
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), mensaje
        else:
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No llevas eso."

    # ABRIR
    if verbo == "abrir":
        if objeto is None or objeto == "":
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "¿Abrir qué?"

        objetivo = objeto.strip().lower()

        if hab == 4 and objetivo in ["alacena", "la alacena"]:
            if cond[2] == "s":
                # marcar la alacena como abierta
                cond[4] = "s"
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), "Una rata salta, te intenta morder, pero gracias a la armadura lo único que consigue es romperse los dientes."
            else:
                return morir_por_rata()

        return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No parece que puedas abrir eso."

    # MOVERSE
    if verbo == "ir":
        direccion = objeto  # "n", "s", "bajar", "subir", etc.

        # Cada habitación define sus salidas válidas y, en algunos casos,
        # condiciones para poder atravesarlas.
        if hab == 1:
            if direccion == "s":
                if cond[1] == "s":
                    habitacion_actual = 2
                    return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
                else:
                    return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No puedes ir hasta que empiece la aventura."
            else:
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No puedes ir en esa dirección."

        elif hab == 2:
            if direccion == "n":
                habitacion_actual = 1
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
            elif direccion in ["bajar"]:
                habitacion_actual = 3
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
            else:
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No puedes ir en esa dirección."

        elif hab == 3:
            # Zaguán: punto central con varias salidas.
            if direccion in ["subir"]:
                habitacion_actual = 2
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
            elif direccion == "n":
                habitacion_actual = 4
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
            elif direccion == "s":
                habitacion_actual = 6
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
            elif direccion == "e":
                habitacion_actual = 7
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
            else:
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No puedes ir en esa dirección."
        
        elif hab == 4:
            # Cocina: acceso al norte hacia el almacén y al sur de vuelta.
            if direccion in ["n"]:
                habitacion_actual = 5
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
            elif direccion == "s":
                habitacion_actual = 3
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
            else:
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No puedes ir en esa dirección."
            
        elif hab == 5:
            # Cuarto de la armadura: solo se vuelve al sur.
            if direccion == "s":
                habitacion_actual = 4
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
            else:
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No puedes ir en esa dirección."       

        elif hab == 6:
            # Despensa: únicamente regresa al zaguán.
            if direccion == "n":
                habitacion_actual = 3
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
            else:
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No puedes ir en esa dirección."       

        elif hab == 7:
            # Portalón: oeste al zaguán, este hacia el exterior condicionado por el libro.
            if direccion == "o":
                habitacion_actual = 3
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
            elif direccion == "e":
                if cond[1] == "s":
                    habitacion_actual = 2
                    return habitacion_actual, descripcion_con_objetos(habitacion_actual), None
                else:
                    return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No puedes ir hasta que empiece la aventura."
            else:
                return habitacion_actual, descripcion_con_objetos(habitacion_actual), "No puedes ir en esa dirección."       
                 
        else:
            return habitacion_actual, descripcion_con_objetos(habitacion_actual), "Te quedas donde estás, confundido."

    # FIN DEL JUEGO
    if verbo == "fin":
        mensaje_final = "Gracias por jugar, caballero andante."
        cerrar_juego_despues(mensaje_final)
        return habitacion_actual, descripcion_con_objetos(habitacion_actual), mensaje_final

    # Cualquier otra cosa
    return habitacion_actual, descripcion_con_objetos(habitacion_actual), "¿Cómo dices?"


# ---------------------------
# 5. INTERFAZ TKINTER
# ---------------------------

# Configuración de la ventana principal y su apariencia.
fondo = tk.Tk()
fondo.title("Don Quijote (por martiper)")
fondo.configure(background="black")

# Centrar ventana 800x640
ancho_pantalla = fondo.winfo_screenwidth()
alto_pantalla = fondo.winfo_screenheight()
x = (ancho_pantalla - 800) // 2
y = (alto_pantalla - 640) // 2
fondo.geometry(f"800x640+{x}+{y}")

frase_var = tk.StringVar()

def cargar_imagen_segura(ruta):
    # Intentamos primero la ruta tal cual (por si ejecutas desde la carpeta del proyecto).
    try:
        return tk.PhotoImage(file=ruta)
    except tk.TclError:
        pass

    # Si falla, intentamos resolver la ruta relativa al propio archivo .py
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        ruta_abs = os.path.join(base, ruta)
        return tk.PhotoImage(file=ruta_abs)
    except tk.TclError:
        return None

# Cargar imagen inicial asociada a la habitación actual.
foto_actual = cargar_imagen_segura(img[habitacion_actual])

imagen = tk.Label(
    fondo,
    bg="black",
    image=foto_actual
)
imagen.foto_actual = foto_actual  # evitar que el recolector de basura elimine la imagen
if foto_actual is None:
    imagen.config(text="(imagen no encontrada)", fg="white", font=("Verdana", 14))
imagen.pack(fill=tk.BOTH, expand=True, pady=(20, 10))  # Aumentar el margen superior

# Zona de texto con la narrativa de la sala y mensajes adicionales.
texto = tk.Label(
    fondo,
    text=descripcion_con_objetos(habitacion_actual),
    fg="white",
    bg="black",
    justify="center",
    wraplength=760,
    height=8,
    font=("Verdana", 18)
)
texto.pack(fill=tk.BOTH, expand=True)

entrada = tk.Entry(
    fondo,
    fg="green",
    bg="black",
    justify="left",
    font=("Verdana", 18),
    textvariable=frase_var,
    insertbackground="green"  # color del cursor
)
entrada.pack(fill=tk.BOTH, expand=True)


def mostrar_pantalla_muerte(mensaje):
    """
    Muestra el mensaje de muerte y espera una tecla para reiniciar la partida.
    """
    texto.config(text=mensaje)
    entrada.config(state="disabled")
    entrada.delete(0, tk.END)
    fondo.bind("<Key>", manejar_tecla_reinicio)


def manejar_tecla_reinicio(event):
    """
    Reinicia todos los estados del juego y devuelve el foco al prompt.
    """
    global estado_muerte
    fondo.unbind("<Key>")
    restablecer_estado_inicial()
    estado_muerte = False
    entrada.config(state="normal")
    refrescar_pantalla(habitacion_actual, descripcion_con_objetos(habitacion_actual), None)
    entrada.delete(0, tk.END)
    entrada.insert(0, ">> ")
    entrada.focus_set()


def refrescar_pantalla(nueva_hab, descripcion_sala, mensaje_extra=None):
    """
    Redibuja imagen y texto.
    Si hay mensaje_extra (p. ej. resultado de 'examinar'), mostramos la
    descripción base de la sala (txt_base) y añadimos el mensaje_extra,
    para evitar duplicados cuando la acción también revela objetos.
    En caso contrario, usamos la descripción dinámica completa.
    """
    global foto_actual
    # Actualizamos la imagen de acuerdo con la habitación destino.
    foto_actual = cargar_imagen_segura(img[nueva_hab])
    if foto_actual:
        imagen.config(image=foto_actual, text="")
        imagen.foto_actual = foto_actual
    else:
        imagen.config(image="", text=f"[Imagen {nueva_hab} no disponible]", fg="white", font=("Verdana", 14))

    # Si hay mensaje_extra preferimos mostrar la descripción base (sin la lista dinámica
    # de objetos) y añadir el mensaje, para evitar repetir la misma información.
    if mensaje_extra:
        base = txt_base[nueva_hab]
        texto_completo = base + "\n\n" + mensaje_extra
    else:
        # comportamiento por defecto: descripción dinámica con objetos
        base = descripcion_con_objetos(nueva_hab)
        texto_completo = base

    # Mostramos la narración final resultante.
    texto.config(text=texto_completo)


def cerrar_juego_despues(mensaje_final):
    # Muestra el mensaje final y destruye la ventana tras un breve retardo.
    texto.config(text=mensaje_final)
    fondo.after(500, fondo.destroy)


def limpiar_prompt(contenido):
    # Permite al jugador escribir con o sin el prompt ">>".
    limpio = contenido.strip()
    if limpio.startswith(">>"):
        limpio = limpio[2:]
    limpio = limpio.strip()
    return limpio


def motor_juego(event):
    global habitacion_actual, estado_muerte

    # Lee el texto del Entry, elimina el prompt si lo hubiera y procesa el comando.
    bruto = frase_var.get()
    comando = limpiar_prompt(bruto)

    entrada.delete(0, tk.END)

    if comando == "":
        # solo refrescar el estado actual sin mensaje extra
        refrescar_pantalla(habitacion_actual, descripcion_con_objetos(habitacion_actual), None)
        entrada.insert(0, ">> ")
        return

    verbo, objeto = parsear(comando)

    if verbo is None:
        refrescar_pantalla(habitacion_actual, descripcion_con_objetos(habitacion_actual), "¿Eh?")
        entrada.insert(0, ">> ")
        return

    nueva_hab, descripcion_sala, mensaje_extra = ejecutar_comando(verbo, objeto)

    if estado_muerte:
        mensaje = mensaje_extra or "Una rata salta y te muerde. Estas muerto.\nPulsa una tecla ..."
        mostrar_pantalla_muerte(mensaje)
        return

    refrescar_pantalla(nueva_hab, descripcion_sala, mensaje_extra)

    entrada.insert(0, ">> ")


# ---------------------------
# 6. INICIO DEL JUEGO
# ---------------------------

# Dejamos el prompt listo, enfocamos la entrada y conectamos la tecla Enter
# con el motor principal. Finalmente iniciamos el bucle de eventos de Tkinter.
entrada.insert(0, ">> ")
entrada.focus_set()
entrada.bind("<Return>", motor_juego)

fondo.mainloop()
