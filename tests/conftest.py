"""
Coordenadas fixas para evitar dependência de rede nos testes (sem chamar o
geocoder) e pessoas fictícias usadas como fixtures.
"""
BH = {"lat": -19.9167, "lng": -43.9333, "tz_str": "America/Sao_Paulo"}
SP = {"lat": -23.5505, "lng": -46.6333, "tz_str": "America/Sao_Paulo"}

ANA = {"nome": "Ana", "data": "12/03/1990", "hora": "14:30", "local": "Belo Horizonte, MG", **BH}
BRUNO = {"nome": "Bruno", "data": "25/07/1992", "hora": "09:15", "local": "São Paulo, SP", **SP}
