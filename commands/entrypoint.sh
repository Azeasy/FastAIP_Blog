#!/bin/bash

check_vars () {
    var_names=("$@")
    for var_name in "${var_names[@]}"; do
        if [[ -z "${!var_name}" ]];
        then
            echo "Warning: ${var_name} is unset."
            var_unset=true            
        fi
    done
    if [[ -n "$var_unset" ]];
    then
        return 1
    else
        return 0
    fi
}

exec "$@"
