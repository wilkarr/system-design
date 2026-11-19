from actividad import Almacen, Publicacion, mas_recientes


class FeedEnEscritura:
    def __init__(self):
        self.almacen = Almacen()
        self.seguidores = {}

    def seguir(self, estudiante, autor):
        if autor not in self.seguidores:
            self.seguidores[autor] = []
        if estudiante not in self.seguidores[autor]:
            self.seguidores[autor].append(estudiante)

    def publicar(self, publicacion):
        for estudiante in self.seguidores.get(publicacion.autor, []):
            self.almacen.agregar(f"feed:{estudiante}", publicacion)

    def leer(self, estudiante, cantidad=10):
        publicaciones = self.almacen.leer(f"feed:{estudiante}")
        return mas_recientes(publicaciones, cantidad)


class FeedEnLectura:
    def __init__(self):
        self.almacen = Almacen()
        self.seguidos = {}

    def seguir(self, estudiante, autor):
        if estudiante not in self.seguidos:
            self.seguidos[estudiante] = []
        if autor not in self.seguidos[estudiante]:
            self.seguidos[estudiante].append(autor)

    def publicar(self, publicacion):
        self.almacen.agregar(f"autor:{publicacion.autor}", publicacion)

    def leer(self, estudiante, cantidad=10):
        todas = []
        for autor in self.seguidos.get(estudiante, []):
            todas.extend(self.almacen.leer(f"autor:{autor}"))
        return mas_recientes(todas, cantidad)


def simular(feed):
    for i in range(10):
        feed.seguir("hincha-" + str(i), "futbol-arquitectura")
    for i in range(8000):
        feed.seguir("estudiante-" + str(i), "final-campeonato")
    for i in range(300):
        feed.seguir("ana", "equipo-" + str(i))

    feed.publicar(Publicacion("p1", "futbol-arquitectura", 100, "Partido el jueves 18:00"))
    print("  Escrituras despues del equipo de arquitectura:", feed.almacen.escrituras)
    feed.publicar(Publicacion("p2", "final-campeonato", 200, "La final es el sabado"))
    print("  Escrituras despues de la final:", feed.almacen.escrituras)

    for i in range(300):
        feed.publicar(Publicacion("e" + str(i), "equipo-" + str(i), 300 + i, "Entrenamiento"))
    antes = feed.almacen.lecturas
    primeras = feed.leer("ana", 3)
    print("  ana lee su feed:", primeras, "con", feed.almacen.lecturas - antes, "lecturas")
    print("  Escrituras en total:", feed.almacen.escrituras)


if __name__ == "__main__":
    print("Fan-out on write:")
    simular(FeedEnEscritura())
    print("Fan-out on read:")
    simular(FeedEnLectura())