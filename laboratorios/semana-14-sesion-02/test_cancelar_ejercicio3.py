"""Ejercicio 3: las pruebas de cancelar. Sin pruebas de partida: las
escribes tu, decidiendo de que tipo es cada una.

    pytest test_cancelar_ejercicio3.py --durations=0
"""

import pytest

from repositorio import RepositorioEnMemoria, RepositorioSQLite
from servicio import ServicioDeReservas


def test_cancelar_con_anticipacion_borra_sin_penalizacion():
    repo = RepositorioEnMemoria()
    servicio = ServicioDeReservas(repo)
    servicio.reservar("r1", "ana", "2026-11-17")
    servicio.cancelar("r1", 1440)
    assert repo.buscar("r1") is None
    assert repo.puntos_de("ana") == 0


def test_cancelar_en_tramo_medio_suma_un_punto():
    repo = RepositorioEnMemoria()
    servicio = ServicioDeReservas(repo)
    servicio.reservar("r1", "ana", "2026-11-17")
    servicio.cancelar("r1", 120)
    assert repo.buscar("r1") is None
    assert repo.puntos_de("ana") == 1


def test_cancelar_tarde_suma_dos_puntos():
    repo = RepositorioEnMemoria()
    servicio = ServicioDeReservas(repo)
    servicio.reservar("r1", "ana", "2026-11-17")
    servicio.cancelar("r1", 60)
    assert repo.buscar("r1") is None
    assert repo.puntos_de("ana") == 2


def test_cancelar_reserva_inexistente_lanza_error():
    servicio = ServicioDeReservas(RepositorioEnMemoria())
    with pytest.raises(ValueError, match="reserva desconocida"):
        servicio.cancelar("no-existe", 300)


def test_cancelar_acumula_puntos_y_bloquea_al_estudiante():
    servicio = ServicioDeReservas(RepositorioEnMemoria())
    servicio.reservar("r1", "ana", "2026-11-17")
    servicio.cancelar("r1", 30)
    servicio.reservar("r2", "ana", "2026-11-18")
    servicio.cancelar("r2", 300)
    with pytest.raises(ValueError, match="estudiante bloqueado"):
        servicio.reservar("r3", "ana", "2026-11-19")


def test_cancelar_en_sqlite_solo_borra_la_reserva_indicada():
    repo = RepositorioSQLite(":memory:")
    servicio = ServicioDeReservas(repo)
    try:
        servicio.reservar("r1", "ana", "2026-11-16")
        servicio.reservar("r2", "ana", "2026-11-17")
        servicio.reservar("r3", "ana", "2026-11-18")
        servicio.cancelar("r2", 3000)
        assert repo.buscar("r2") is None
        assert repo.buscar("r1") == ("ana", "2026-11-16")
        assert repo.buscar("r3") == ("ana", "2026-11-18")
        servicio.reservar("r4", "ana", "2026-11-19")
        with pytest.raises(ValueError, match="cupo semanal agotado"):
            servicio.reservar("r5", "ana", "2026-11-20")
    finally:
        repo.cerrar()


def test_cancelar_en_sqlite_persiste_puntos_de_penalizacion():
    repo = RepositorioSQLite(":memory:")
    servicio = ServicioDeReservas(repo)
    try:
        servicio.reservar("r1", "ana", "2026-11-17")
        servicio.cancelar("r1", 30)
        assert repo.puntos_de("ana") == 2
    finally:
        repo.cerrar()
