# Ladybug packages

Radiation calculations use external CPython. Geometry conversion and shadow/isovist mesh intersections run inside Rhino with RhinoCommon. Select package versions compatible with each host's actual Python version; external CPython does not supply RhinoCommon.

| Host | Required packages and imports |
| --- | --- |
| External radiation worker | `ladybug-core` (`ladybug`), `ladybug-geometry` (`ladybug_geometry`), `ladybug-radiance` (`ladybug_radiance`) |
| Rhino geometry operations | `ladybug-core`, `ladybug-geometry`, `ladybug-rhino` (`ladybug_rhino`), and RhinoCommon (`Rhino`) |

Use official metadata for [Ladybug core](https://github.com/ladybug-tools/ladybug), [geometry](https://github.com/ladybug-tools/ladybug-geometry), [Rhino integration](https://github.com/ladybug-tools/ladybug-rhino), and [Radiance integration](https://github.com/ladybug-tools/ladybug-radiance). The unrelated package named `ladybug` is not a substitute for `ladybug-core`.

For installation, lock direct and transitive versions separately for each host. Identify external environments by Python version, platform, and lock hash; reuse a match or create a managed environment and install through its `python -m pip`. Use Rhino's supported package mechanism or a compatible managed package directory for Rhino. Do not add an external environment's complete `site-packages` to Rhino's search path.

Check imports and dependency consistency in the actual hosts. Record versions, lock paths and hashes, and failures. A Rhino 7-or-later installation alone does not establish Python/package compatibility; report any unsupported combination without declaring the analysis ready.
