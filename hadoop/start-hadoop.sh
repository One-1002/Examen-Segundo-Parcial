#!/bin/bash
set -e

echo "Iniciando configuracion SSH de Hadoop..."

mkdir -p /shared/ssh
chown hadoop:hadoop /shared/ssh

mkdir -p /data/output
chown -R hadoop:hadoop /data/output

mkdir -p /home/hadoop/.ssh
mkdir -p /run/sshd

# Generar llaves si todavía no existen
if [ ! -f /shared/ssh/id_ed25519 ]; then
    su -s /bin/bash hadoop -c \
      'ssh-keygen -t ed25519 -N "" -f /shared/ssh/id_ed25519'
fi

# Autorizar la llave publica
cp /shared/ssh/id_ed25519.pub /home/hadoop/.ssh/authorized_keys

chown -R hadoop:hadoop /home/hadoop/.ssh
chmod 700 /home/hadoop/.ssh
chmod 600 /home/hadoop/.ssh/authorized_keys
chmod 600 /shared/ssh/id_ed25519
chmod 644 /shared/ssh/id_ed25519.pub

echo "Iniciando servidor SSH..."
/usr/sbin/sshd

echo "Hadoop esta listo."
exec tail -f /dev/null