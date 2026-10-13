#!/bin/bash
# Runs the add-on's plain-java tests (pure logic only; game hooks are checked in game). Same classpath as build.sh.
set -euo pipefail
cd "$(dirname "$0")"
PRISM_LIBS=${PRISM_LIBS:-C:/Users/Dylan/AppData/Roaming/PrismLauncher/libraries}
SERVER_DATA=${SERVER_DATA:-C:/Users/Dylan/Documents/Minecraft server/server-test/data}
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$(pwd -W 2>/dev/null || pwd):/w" -v "$PRISM_LIBS:/libs:ro" -v "$SERVER_DATA:/data:ro" -w /w \
  eclipse-temurin:17-jdk sh -c '
    set -e
    CP=$(find /libs -name "*.jar" ! -name "minecraft-*-client.jar" ! -name "*-extra.jar" ! -name "*-slim.jar" \
           ! -path "*/forge/1.20.1-47.4.10/*" | tr "\n" ":")
    CP="$CP$(ls /data/libraries/net/minecraftforge/forge/1.20.1-47.4.23/forge-1.20.1-47.4.23-universal.jar):$(ls /data/mods/*.jar compile-libs/*.jar | tr "\n" ":")"
    rm -rf /tmp/t && mkdir -p /tmp/t
    javac --release 17 -proc:none -nowarn -cp "$CP" -d /tmp/t $(find src test -name "*.java")
    for t in $(cd test && find . -name "*Test.java" | sed "s|^\./||; s|\.java$||; s|/|.|g"); do java -cp "/tmp/t:$CP" "$t"; done
  '
