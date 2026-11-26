"""Ejercicio 1: la misma cobertura, en la base de la piramide. Empieza
vacio: se escribe en vivo.

Por cada prueba de punta a punta de test_suite_heredada.py que se pueda
bajar de nivel, una prueba unitaria del servicio (con RepositorioEnMemoria)
o una de integracion (con RepositorioSQLite o con la API), y una sola
prueba de punta a punta que recorra el camino completo.

    pytest test_rapidas_ejercicio1.py --durations=0
"""

import pytest

from api import ApiDeReservas
from dominio import puntos_por_cancelar, semana_de
from entorno_e2e import NavegadorSimulado
from repositorio import RepositorioEnMemoria, RepositorioSQLite
from servicio import ServicioDeReservas


@pytest.fixture
def servicio():
    return ServicioDeReservas(repositorio=RepositorioEnMemoria())


def test_la_semana_va_de_lunes_a_domingo():
    assert semana_de("2026-11-16") == semana_de("2026-11-22")
    assert semana_de("2026-11-22") != semana_de("2026-11-23")


def test_los_tramos_de_puntos():
    assert puntos_por_cancelar(1440) == 0
    assert puntos_por_cancelar(120) == 1
    assert puntos_por_cancelar(119) == 2


def test_reservar_una_cancha(servicio):
    servicio.reservar("r1", "pedro", "2026-11-26")
    assert servicio.repositorio.buscar("r1") == ("pedro", "2026-11-26")


def test_la_cuarta_reserva_se_rechaza(servicio):
    servicio.reservar("r1", "pedro", "2026-11-26")
    servicio.reservar("r2", "pedro", "2026-11-27")
    servicio.reservar("r3", "pedro", "2026-11-28")
    assert servicio.motivo_de_rechazo("pedro", "2026-11-29") == "cupo semanal agotado"
    with pytest.raises(ValueError, match="cupo semanal agotado"):
        servicio.reservar("r4", "pedro", "2026-11-29")


def test_la_cuarta_reserva_diferente_semana_aceptada(servicio):
    servicio.reservar("r1", "pedro", "2026-11-26")
    servicio.reservar("r2", "pedro", "2026-11-27")
    servicio.reservar("r3", "pedro", "2026-11-28")
    assert servicio.motivo_de_rechazo("pedro", "2026-12-01") is None
    servicio.reservar("r4", "pedro", "2026-12-01")
    assert servicio.repositorio.buscar("r4") == ("pedro", "2026-12-01")


def test_el_cupo_es_de_cada_estudiante(servicio):
    servicio.reservar("r1", "pedro", "2026-11-26")
    servicio.reservar("r2", "pedro", "2026-11-27")
    servicio.reservar("r3", "pedro", "2026-11-28")
    assert servicio.motivo_de_rechazo("ana", "2026-11-28") is None
    servicio.reservar("r4", "ana", "2026-11-28")
    assert servicio.repositorio.buscar("r4") == ("ana", "2026-11-28")


def test_cancelar_una_reserva(servicio):
    servicio.reservar("r1", "pedro", "2026-11-26")
    servicio.cancelar("r1", 3000)
    assert servicio.repositorio.buscar("r1") is None


def test_cancelar_tarde_suma_puntos(servicio):
    servicio.reservar("r1", "pedro", "2026-11-26")
    servicio.cancelar("r1", 30)
    assert servicio.repositorio.puntos_de("pedro") == 2


def test_cancelar_con_tiempo_no_suma_puntos(servicio):
    servicio.reservar("r1", "pedro", "2026-11-26")
    servicio.cancelar("r1", 3000)
    assert servicio.repositorio.puntos_de("pedro") == 0


def test_tres_puntos_bloquean(servicio):
    servicio.reservar("r1", "pedro", "2026-11-26")
    servicio.cancelar("r1", 30)
    servicio.reservar("r2", "pedro", "2026-11-27")
    servicio.cancelar("r2", 600)
    assert servicio.motivo_de_rechazo("pedro", "2026-11-28") == "estudiante bloqueado"
    with pytest.raises(ValueError, match="estudiante bloqueado"):
        servicio.reservar("r3", "pedro", "2026-11-28")


def test_cancelar_una_reserva_que_no_existe(servicio):
    with pytest.raises(ValueError, match="reserva desconocida"):
        servicio.cancelar("reserva-inexistente", 3000)


def test_cancelar_libera_el_cupo(servicio):
    servicio.reservar("r1", "pedro", "2026-11-26")
    servicio.reservar("r2", "pedro", "2026-11-27")
    servicio.reservar("r3", "pedro", "2026-11-28")
    servicio.cancelar("r3", 3000)
    servicio.reservar("r4", "pedro", "2026-11-29")
    assert servicio.repositorio.buscar("r4") == ("pedro", "2026-11-29")


def test_api_cancelar_desconocida_404():
    repo = RepositorioSQLite(":memory:")
    api = ApiDeReservas(ServicioDeReservas(repositorio=repo))
    respuesta = api.manejar({
        "metodo": "DELETE",
        "ruta": "/reservas/reserva-inexistente",
        "cuerpo": {
            "minutos_de_anticipacion": 90
        }
    })
    repo.cerrar()
    assert respuesta["estado"] == 404
    assert respuesta["cuerpo"]["error"] == "reserva desconocida"


def test_api_reservar_y_rechazar_cupo_409():
    repo = RepositorioSQLite(":memory:")
    api = ApiDeReservas(ServicioDeReservas(repositorio=repo))
    assert api.manejar({
        "metodo": "POST",
        "ruta": "/reservas",
        "cuerpo": {"id": "r1", "estudiante": "pedro", "fecha": "2026-11-26"}
    })["estado"] == 201
    assert api.manejar({
        "metodo": "POST",
        "ruta": "/reservas",
        "cuerpo": {"id": "r2", "estudiante": "pedro", "fecha": "2026-11-27"}
    })["estado"] == 201
    assert api.manejar({
        "metodo": "POST",
        "ruta": "/reservas",
        "cuerpo": {"id": "r3", "estudiante": "pedro", "fecha": "2026-11-28"}
    })["estado"] == 201
    respuesta = api.manejar({
        "metodo": "POST",
        "ruta": "/reservas",
        "cuerpo": {"id": "r4", "estudiante": "pedro", "fecha": "2026-11-29"}
    })
    repo.cerrar()
    assert respuesta["estado"] == 409
    assert respuesta["cuerpo"]["error"] == "cupo semanal agotado"


def test_reservar_cancelar_ver_puntos():
    navegador = NavegadorSimulado()
    navegador.iniciar_sesion("pedro")
    assert navegador.reservar("r1", "2026-11-26")["estado"] == 201
    assert navegador.cancelar("r1", 30)["estado"] == 200
    assert navegador.ver_puntos() == 2
