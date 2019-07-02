#!/bin/sh



tar -C server -c world --add-file=server.properties |pigz > server-1.14.x-myself-$(date +%F-%H-%M-%S).tar.gz
