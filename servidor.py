import sys
import uuid
from random import randint 
from PyQt4 import QtGui, QtCore, uic
from xmlrpc.server import SimpleXMLRPCServer

class Serpiente():
    def __init__(self):
        rojo, verde, azul = randint(0,255), randint(0,255), randint(0,255)
        self.Id = str(uuid.uuid4())[:9]
        self.color = {"r": rojo, "g": verde, "b": azul}
        self.ruta = []
        self.celdas = []
        self.tam = len(self.celdas)
        self.direccion = "Abajo"

        def diccionario_Serpiente(self):
            diccionario = {
                'Id': self.Id,
                'ruta': self.ruta, 
                'color': self.color
            }
            return diccionario

class VentanaServidor(QtGui.QMainWindow):

    def __init__(self):
        super(VentanaServidor, self).__init__()
        uic.loadUi('servidor.ui', self)
        self.setWindowTitle("Juego Snake")
        self.setWindowIcon(QtGui.QIcon("snake.png"))
        self.boton_fin.hide()
        self.juego_empezado = False
        self.juego_pausado = False
        self.tiempo = None
        self.tiempo_servidor = None
        self.tiempo_ruta = None
        self.lista_serpientes = []
        self.expandir_cuadros_tabla()
        self.llenar_tabla()
        self.tabla.setSelectionMode(QtGui.QTableWidget.NoSelection)
        self.tabla.setRowCount(self.columnas.value())
        self.tabla.setColumnCount(self.filas.value())
        self.boton_inicia.clicked.connect(self.iniciar_juego)
        self.boton_servidor.clicked.connect(self.inicializar_servidor)
        self.boton_fin.clicked.connect(self.terminar_juego)
        self.columnas.valueChanged.connect(self.actualizar_tabla)
        self.filas.valueChanged.connect(self.actualizar_tabla)
        self.espera.valueChanged.connect(self.actualizar_tiempo)
        self.timeout.valueChanged.connect(self.actualizar_timeout)
        self.show()

    def crea_serpiente(self):
        serpiente_nueva = Serpiente()
        creada = False
        while not creada:
            creada = True
            uno = randint(1, self.tabla.rowCount()/2)
            dos = uno + 1
            tres = uno + 2
            cuatro = uno + 3
            ancho = randint(1, self.tabla.columnCount()-1)
            cabeza, cuerpo_1, cuerpo_2, cuerpo_3 = [uno, ancho], [dos, ancho], [tres, ancho], [cuatro, ancho]
            for serpiente in self.lista_serpientes:
                if cabeza in serpiente.celdas or cuerpo_1 in serpiente.celdas or cuerpo_2 in serpiente.celdas or cuerpo_3 in serpiente.celdas:
                    creada = False
                    break
            serpiente_nueva.celdas = [cabeza, cuerpo_1, cuerpo_2, cuerpo_3]
            self.lista_serpientes.append(serpiente_nueva)
            return serpiente_nueva

    def lista_Serpientes(self):
        lista = list()
        for serpiente in self.lista_serpientes:
            lista.append(serpiente.diccionario_Serpiente())
        return lista

    def inicializar_servidor(self):
        direccion = self.url.text()
        puerto = self.puerto.value()
        self.servidor = SimpleXMLRPCServer((direccion, 0))
        puerto = self.servidor.server_address[1] 
        self.puerto.setValue(puerto)
        self.url.setReadOnly(True)
        self.puerto.setReadOnly(True)
        self.boton_servidor.setEnabled(False)
        self.servidor.register_function(self.estado_del_juego)
        self.servidor.register_function(self.yo_juego)
        self.servidor.register_function(self.cambia_direccion)
        self.servidor.register_function(self.ping)
        self.servidor.timeout = 0
        self.tiempo_servidor = QtCore.QTimer(self)
        self.tiempo_servidor.timeout.connect(self.revisa_peticiones) 
        self.tiempo_servidor.start(self.servidor.timeout)
        
    def iniciar_juego(self):
        if not self.juego_empezado:
            self.boton_fin.show()
            self.crea_serpiente()
            self.boton_inicia.setText("Pausar el Juego")
            self.llenar_tabla()
            self.dibujar_serpientes()
            self.tiempo = QtCore.QTimer(self)
            self.tiempo.timeout.connect(self.mover_serpientes)
            self.tiempo.start(250)
            self.tiempo.setInterval(self.espera.value())
            self.tiempo_ruta = QtCore.QTimer(self)
            self.tiempo_ruta.timeout.connect(self.actualizar_ruta)
            self.tiempo_ruta.start(150)
            self.tabla.installEventFilter(self)
            self.juego_empezado = True 
        elif self.juego_empezado and not self.juego_pausado:
            self.tiempo.stop()
            self.juego_pausado = True
            self.boton_inicia.setText("Reanudar el Juego") 
        elif self.juego_pausado:
            self.tiempo.start()
            self.juego_pausado = False
            self.boton_inicia.setText("Pausar el Juego")

    def terminar_juego(self):
        self.lista_serpientes = []
        self.tiempo.stop()
        self.juego_empezado = False
        self.boton_fin.hide() 
        self.boton_inicia.setText("Inicia Juego")
        self.llenar_tabla()

    def actualizar_tiempo(self):
        valor = self.espera.value()
        self.tiempo.setInterval(valor)

    def revisa_peticiones(self):
        self.servidor.handle_request()

    def eventFilter(self, source, event):

        if (event.type() == QtCore.QEvent.KeyPress and
            source is self.tabla):
                key = event.key()
                if (key == QtCore.Qt.Key_Up and
                    source is self.tabla):
                    for serpiente in self.lista_serpientes:
                        if serpiente.direccion is not "Abajo":
                            serpiente.direccion = "Arriba"
                elif (key == QtCore.Qt.Key_Down and
                    source is self.tabla):
                    for serpiente in self.lista_serpientes:
                        if serpiente.direccion is not "Arriba":
                            serpiente.direccion = "Abajo"
                elif (key == QtCore.Qt.Key_Right and
                    source is self.tabla):
                    for serpiente in self.lista_serpientes:
                        if serpiente.direccion is not "Izquierda":
                            serpiente.direccion = "Derecha"
                elif (key == QtCore.Qt.Key_Left and
                    source is self.tabla):
                    for serpiente in self.lista_serpientes:
                        if serpiente.direccion is not "Derecha":
                            serpiente.direccion = "Izquierda"
        return QtGui.QMainWindow.eventFilter(self, source, event)

    def dibujar_serpientes(self):
        for serpiente in self.lista_serpientes:
            for seccion_corporal in serpiente.celdas:
                self.tabla.item(seccion_corporal[0], seccion_corporal[1]).setBackground(QtGui.QColor(serpiente.color['r'], serpiente.color['g'], serpiente.color['b']))

    def colision(self, serpiente):
        for seccion_corporal in serpiente.celdas[0:len(serpiente.celdas)-2]:
            if serpiente.celdas[-1][0] == seccion_corporal[0] and serpiente.celdas[-1][1] == seccion_corporal[1]:
                ventana = ventanaEmergente().exec_()
                return True
        return False

    def moriste(self, revisa):
        for serpiente in self.lista_serpientes:
            if revisa.Id != revisa.Id:
                for seccion_corporal in serpiente.celdas[:]: 
                    if revisa.celdas[-1][0] == seccion_corporal[0] and revisa.celdas[-1][1] == seccion_corporal[1]:
                        self.lista_serpientes.remove(revisa)

    def mover_serpientes(self):
        for serpiente in self.lista_serpientes:
            if self.colision(serpiente):
               self.terminar_juego()
            self.tabla.item(serpiente.celdas[0][0],serpiente.celdas[0][1]).setBackground(QtGui.QColor(255,255,255))
            x = 0 
            for tupla in serpiente.celdas[0: len(serpiente.celdas)-1]:
                x += 1
                tupla[0] = serpiente.celdas[x][0]
                tupla[1] = serpiente.celdas[x][1]
            if serpiente.direccion is "Abajo":
                if serpiente.celdas[-1][0] + 1 < self.tabla.rowCount():
                    serpiente.celdas[-1][0] += 1
                else:
                    serpiente.celdas[-1][0] = 0
            if serpiente.direccion is "Derecha":
                if serpiente.celdas[-1][1] + 1 < self.tabla.columnCount():
                    serpiente.celdas[-1][1] += 1
                else:
                    serpiente.celdas[-1][1] = 0
            if serpiente.direccion is "Arriba":
                if serpiente.celdas[-1][0] != 0:
                    serpiente.celdas[-1][0] -= 1
                else:
                    serpiente.celdas[-1][0] = self.tabla.rowCount()-1
            if serpiente.direccion is "Izquierda":
                if serpiente.celdas[-1][1] != 0:
                    serpiente.celdas[-1][1] -= 1
                else:
                    serpiente.celdas[-1][1] = self.tabla.columnCount()-1
        self.dibujar_serpientes()

     # ----- Funciones para Cliente ------ #

    def ping(self):
        return "¡Pong!"

    def yo_juego(self):
        serpiente_nueva = self.crea_serpiente()
        diccionario = {
        "Id": serpiente_nueva.Id, 
        "color": serpiente_nueva.color
        }
        return diccionario    

    def estado_del_juego(self):
        
        diccionario = dict()
        diccionario = {
            'espera': self.servidor.timeout, 
            'tamX': self.tabla.columnCount(),
            'tamY': self.tabla.rowCount(),
            'viboras': self.lista_serpientes()
        }
        return diccionario 

    def cambia_direccion(self, identificador, numero):
        
        for serpiente in self.lista_serpientes:
            if serpiente.Id == identificador:
                if numero == 0:
                    if serpiente.direccion is not "Abajo": 
                        serpiente.direccion = "Arriba"
                if numero == 1:
                    if serpiente.direccion is not "Izquierda":
                        serpiente.direccion = "Derecha"
                if numero == 2: 
                    if serpiente.direccion is not "Arriba":
                        serpiente.direccion = "Abajo"
                if numero == 3: 
                    if serpiente.direccion is not "Derecha":
                        serpiente.direccion = "Izquierda"
        return True 

    def actualizar_ruta(self):
        for serpiente in self.lista_serpientes:
            serpiente.ruta = []
            for celda in serpiente.celdas:
                serpiente.ruta.append((celda[0], celda[1]))

    def actualizar_timeout(self):
        self.servidor.timeout = self.timeout.value()
        self.tiempo_servidor.setInterval(self.timeout.value())

    def llenar_tabla(self):
        for i in range(self.tabla.rowCount()):
            for j in range(self.tabla.columnCount()):
                self.tabla.setItem(i,j, QtGui.QTableWidgetItem())
                self.tabla.item(i,j).setBackground(QtGui.QColor(255,255,255))

    def expandir_cuadros_tabla(self):
        self.tabla.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.tabla.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def actualizar_tabla(self):
        
        num_filas = self.filas.value()
        num_columnas = self.columnas.value()
        self.tabla.setRowCount(num_filas)
        self.tabla.setColumnCount(num_columnas)
        self.llenar_tabla()

class ventanaEmergente(QtGui.QDialog):
    def __init__(self, parent = None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Game Over")
        self.setWindowIcon(QtGui.QIcon("gameOver.jpg"))
        self.mensaje = QtGui.QLabel("¡Estuviste cerca! \nprueba de nuevo :)", self)
        self.mensaje.setFont(QtGui.QFont('Courier', 15))
        self.mensaje.resize(self.mensaje.sizeHint())
        self.mensaje.setStyleSheet("QLabel { color : #9999ff; }")
        self.mensaje.move(60, 50) 
        self.mensaje.show()
        
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ventana = VentanaServidor()
    sys.exit(app.exec_())