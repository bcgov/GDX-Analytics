#!/usr/bin/env bash
##################################################
#
# Download latest version of looker jars
#
##################################################
set -e
if [[ -z "${LOOKER_LICENSE}" ]]; then
  echo Enter Looker License
  read LookerLicense
else
  LookerLicense="${LOOKER_LICENSE}"
fi
if [[ -z "${DOWNLOAD_EMAIL}" ]]; then
  echo Enter authorized email address 
  read DownloadEmail
else
  DownloadEmail="${DOWNLOAD_EMAIL}"
fi

Cmd="curl -s -X POST -H 'Content-Type: application/json' -d '{\"lic\": \"$LookerLicense\", \"email\": \"$DownloadEmail\", \"latest\":\"latest\"}' https://apidownload.looker.com/download"
Json=`eval $Cmd`
Url=`echo $Json|perl -pe 's/.*{"url":"(.+?)".*/\1/'`
JarFileName=`echo $Json|perl -pe 's/.*"version_text":"(.+?)".*/\1/'`
echo downloading $JarFileName to looker.jar
curl -Lo looker.jar $Url
DepUrl=`echo $Json|perl -pe 's/.*"depUrl":"(.+?)".*/\1/'`
DepJarFileName=`echo $Json|perl -pe 's/.*"depUrl":".*\/(.+?\.jar).*/\1/'`
echo downloading $DepJarFileName to looker-dependencies.jar
curl -Lo looker-dependencies.jar $DepUrl

