#!/bin/bash
# Builds mimiandroidfix-1.0.0.jar with plain javac (no Gradle needed: the mixin targets
# MIMI's own classes, which aren't obfuscated Minecraft code, so no refmap is required).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p libs
fetch() { [ -f "libs/$(basename "$1")" ] || curl -sfL -o "libs/$(basename "$1")" "$1"; }
fetch https://repo.spongepowered.org/repository/maven-public/org/spongepowered/mixin/0.8.5/mixin-0.8.5.jar
fetch https://repo1.maven.org/maven2/org/apache/commons/commons-lang3/3.12.0/commons-lang3-3.12.0.jar
fetch https://repo1.maven.org/maven2/org/apache/logging/log4j/log4j-api/2.19.0/log4j-api-2.19.0.jar
fetch https://maven.minecraftforge.net/net/minecraftforge/javafmllanguage/1.20.1-47.4.23/javafmllanguage-1.20.1-47.4.23.jar
fetch https://cdn.modrinth.com/data/efSTEGLV/versions/2GXOuCi2/mimimod-1.20.1-4.3.0-forge.jar

JAVA_HOME=${JAVA_HOME:-$(/usr/libexec/java_home)}
CP=$(ls libs/*.jar | tr '\n' ':')
rm -rf build && mkdir -p build/classes
"$JAVA_HOME/bin/javac" --release 17 -proc:none -cp "$CP" -d build/classes $(find src -name '*.java')
cp -R res/. build/classes/
"$JAVA_HOME/bin/jar" --create --file mimiandroidfix-1.0.0.jar --manifest MANIFEST.MF -C build/classes .
rm -rf build
echo "Built mimiandroidfix-1.0.0.jar"
