
# Imagen base
FROM debian:bookworm-slim

# Evitar preguntas durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar Java, Python, SSH y utilidades
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    openssh-server \
    openssh-client \
    curl \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Variables de entorno
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Descargar e instalar Hadoop
RUN mkdir -p /opt/hadoop && \
    curl -fL https://archive.apache.org/dist/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz \
    | tar -xz --strip-components=1 -C /opt/hadoop

# Configurar JAVA_HOME para Hadoop
RUN sed -i "s|^# export JAVA_HOME=.*|export JAVA_HOME=${JAVA_HOME}|" \
    $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# Crear usuario Hadoop
RUN useradd -m -s /bin/bash hadoop

# Preparar SSH
RUN mkdir -p /run/sshd /home/hadoop/.ssh && \
    chown -R hadoop:hadoop /home/hadoop/.ssh && \
    chmod 700 /home/hadoop/.ssh

# Configurar SSH para autenticación mediante llaves
RUN sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' \
    /etc/ssh/sshd_config && \
    sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' \
    /etc/ssh/sshd_config && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config

# Permisos de Hadoop
RUN chown -R hadoop:hadoop /opt/hadoop

# Directorio de trabajo
WORKDIR /home/hadoop

# Puerto SSH
EXPOSE 22

# Iniciar SSH y mantener vivo el contenedor
CMD ["/bin/bash", "-c", "/usr/sbin/sshd && tail -f /dev/null"]

# Imagen base
FROM debian:bookworm-slim

# Evitar preguntas durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar Java, Python, SSH y utilidades
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk \
    python3 \
    python3-pip \
    openssh-server \
    openssh-client \
    curl \
    ca-certificates \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Variables de entorno
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Descargar e instalar Hadoop
RUN mkdir -p /opt/hadoop && \
    curl -fL https://archive.apache.org/dist/hadoop/common/hadoop-3.4.1/hadoop-3.4.1.tar.gz \
    | tar -xz --strip-components=1 -C /opt/hadoop

# Configurar JAVA_HOME para Hadoop
RUN sed -i "s|^# export JAVA_HOME=.*|export JAVA_HOME=${JAVA_HOME}|" \
    $HADOOP_HOME/etc/hadoop/hadoop-env.sh

# Crear usuario Hadoop
RUN useradd -m -s /bin/bash hadoop

# Preparar SSH
RUN mkdir -p /run/sshd /home/hadoop/.ssh && \
    chown -R hadoop:hadoop /home/hadoop/.ssh && \
    chmod 700 /home/hadoop/.ssh

# Configurar SSH para autenticación mediante llaves
RUN sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' \
    /etc/ssh/sshd_config && \
    sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' \
    /etc/ssh/sshd_config && \
    echo "PermitRootLogin no" >> /etc/ssh/sshd_config

# Permisos de Hadoop
RUN chown -R hadoop:hadoop /opt/hadoop

# Directorio de trabajo
WORKDIR /home/hadoop

# Copiar el script de inicio
COPY start-hadoop.sh /usr/local/bin/start-hadoop.sh

# Dar permisos de ejecución al script
RUN chmod +x /usr/local/bin/start-hadoop.sh

# Puerto SSH
EXPOSE 22

# Iniciar Hadoop y SSH
CMD ["/usr/local/bin/start-hadoop.sh"]
