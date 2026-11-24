"""Pruebas del Ejercicio 3: las escriben ustedes, en pareja, una a la vez."""
from recurrentes_ejercicio3 import AgendaDeCancha
from reservas import CalendarioDeCancha


def test_calendario_crea_y_reutiliza_instancia_por_fecha():
    agenda = AgendaDeCancha("cancha-1")
    cal1 = agenda.calendario("2026-11-16")
    cal2 = agenda.calendario("2026-11-16")

    assert isinstance(cal1, CalendarioDeCancha)
    assert cal1 is cal2


def test_reservar_una_semana():
    agenda = AgendaDeCancha("cancha-1")
    res = agenda.reservar_cada_semana("entreno", "equipo_a", "2026-11-16", 10, 12, 1)

    assert res == [("2026-11-16", "reservada")]


def test_reservar_varias_semanas_consecutivas():
    agenda = AgendaDeCancha("cancha-1")
    res = agenda.reservar_cada_semana("entreno", "equipo_a", "2026-11-16", 10, 12, 3)

    assert res == [
        ("2026-11-16", "reservada"),
        ("2026-11-23", "reservada"),
        ("2026-11-30", "reservada"),
    ]

def test_semana_ocupada_se_salta_y_continua():
    agenda = AgendaDeCancha("cancha-1")
    agenda.calendario("2026-11-23").reservar("otra-1", "otro_est", 10, 12)

    res = agenda.reservar_cada_semana("entreno", "equipo_a", "2026-11-16", 10, 12, 3)

    assert res == [
        ("2026-11-16", "reservada"),
        ("2026-11-23", "ocupada"),
        ("2026-11-30", "reservada"),
    ]


def test_semana_excede_limite_diario_devuelve_limite_y_continua():
    agenda = AgendaDeCancha("cancha-1")
    agenda.calendario("2026-11-16").reservar("previa-1", "equipo_a", 7, 9)

    res = agenda.reservar_cada_semana("entreno", "equipo_a", "2026-11-16", 10, 12, 2)

    assert res == [
        ("2026-11-16", "limite"),
        ("2026-11-23", "reservada"),
    ]


def test_cero_semanas_lanza_value_error_sin_reservar():
    agenda = AgendaDeCancha("cancha-1")
    try:
        agenda.reservar_cada_semana("entreno", "equipo_a", "2026-11-16", 10, 12, 0)
        assert False, "Debió lanzar ValueError con 0 semanas"
    except ValueError:
        assert agenda._calendarios == {}


def test_semanas_negativas_lanza_value_error_sin_reservar():
    agenda = AgendaDeCancha("cancha-1")
    try:
        agenda.reservar_cada_semana("entreno", "equipo_a", "2026-11-16", 10, 12, -2)
        assert False, "Debió lanzar ValueError con semanas negativas"
    except ValueError:
        assert agenda._calendarios == {}


def test_mas_de_12_semanas_lanza_value_error_sin_reservar():
    agenda = AgendaDeCancha("cancha-1")
    try:
        agenda.reservar_cada_semana("entreno", "equipo_a", "2026-11-16", 10, 12, 13)
        assert False, "Debió lanzar ValueError con más de 12 semanas"
    except ValueError:
        assert agenda._calendarios == {}