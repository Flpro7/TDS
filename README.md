# TDS

Herramientas mínimas para definir mapas y oleadas de un modo simplificado de tower defense.

## Estructura de datos

- `data/maps/*.json`: Metadatos de cada mapa disponible.
- `data/waves/<mapa>.csv`: Definiciones de oleadas base asociadas a cada mapa.

## Uso rápido

```bash
python main.py
```

El comando anterior abre la demostración interactiva en Pygame.

Para lanzar solo el configurador de mapas y oleadas desde la terminal puedes usar:

```bash
python main.py --mode configurator
# o, si prefieres evitar dependencias de Pygame
python -m tds.menu
```

Ambas opciones muestran el menú de selección de mapas y un resumen de las oleadas con la dificultad ya ajustada.

## Pruebas

```bash
pytest
```
