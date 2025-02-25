#!/bin/bash

# Imprimir mensaje de inicio
echo "Iniciando contenedor ETL Fandit..."

# Verificar si el modo de ejecución automática está activado
if [ "$ENABLE_AUTO_ETL" = "true" ]; then
    echo "Ejecución automática ACTIVADA - El ETL se ejecutará diariamente a las 12:00 (Hora de Madrid)"
    
    # Iniciar el servicio cron en primer plano
    cron -f
else
    echo "Ejecución automática DESACTIVADA - El ETL solo se ejecutará manualmente"
    
    # Mantener el contenedor en ejecución
    tail -f /dev/null
fi