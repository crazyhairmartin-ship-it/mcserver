#!/bin/bash
# Builds fotfmail-1.0.0.jar with plain javac inside a JDK 17 container (no Gradle, nothing installed locally).
# Compiles against Forge's SRG-named Minecraft jar, so vanilla methods are written as m_XXXX_ in the source and
# mixins use remap=false. Needs Prism's libraries (client SRG jar, Forge, mixin) and Ender Mail's jar:
#   PRISM_LIBS   default C:/Users/Dylan/AppData/Roaming/PrismLauncher/libraries
#   SERVER_DATA  default C:/Users/Dylan/Documents/Minecraft server/server/data  (forge universal + mods/EnderMail)
# Regenerate MailboxWood.java first if the wood list changed: python ../../tools/mailbox/make_mailbox.py
set -euo pipefail
cd "$(dirname "$0")"
PRISM_LIBS=${PRISM_LIBS:-C:/Users/Dylan/AppData/Roaming/PrismLauncher/libraries}
SERVER_DATA=${SERVER_DATA:-C:/Users/Dylan/Documents/Minecraft server/server/data}
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$(pwd -W 2>/dev/null || pwd):/w" -v "$PRISM_LIBS:/libs:ro" -v "$SERVER_DATA:/data:ro" -w /w \
  eclipse-temurin:17-jdk sh -c '
    set -e
    CP=$(find /libs -name "*.jar" ! -name "minecraft-*-client.jar" ! -name "*-extra.jar" ! -name "*-slim.jar" \
           ! -path "*/forge/1.20.1-47.4.10/*" | tr "\n" ":")
    CP="$CP$(ls /data/libraries/net/minecraftforge/forge/1.20.1-47.4.23/forge-1.20.1-47.4.23-universal.jar):$(ls /data/mods/*.jar | tr "\n" ":")"
    rm -rf build && mkdir -p build/classes
    javac --release 17 -proc:none -nowarn -cp "$CP" -d build/classes $(find src -name "*.java")
    cp -R res/. build/classes/
    jar --create --file fotfmail-1.0.0.jar --manifest MANIFEST.MF -C build/classes .
    rm -rf build
  '
echo "Built fotfmail-1.0.0.jar"
