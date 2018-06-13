#!/bin/sh -u

#Copyright 2015 Province of British Columbia
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

# This script is based on a public domain script by Viktor Szakats (vszakats.net)

# Upload a file to Amazon AWS S3 using Signature Version 4
#
# docs:
#    https://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html
#
# requires:
#    curl, openssl 1.x, GNU sed, LF EOLs in this file
# usage: 
#    sh s3-upload.sh <<localfile>> <<bucket>> <<remotepath>> <<region>> <<OPTIONAL:storageclass>>
#
# Depends on AWS credentials being set via env:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY


fileLocal="${1:-example-local-file.ext}"
bucket="${2:-example-bucket}"
remotepath="${3:-}" # by default will place in the root of the bucket
region="${4:-ca-central-1}" # optional, will default to ca-central-1
storageClass="${5:-STANDARD}"  # or 'REDUCED_REDUNDANCY'

m_openssl() {
  if [ -f /usr/local/opt/openssl@1.1/bin/openssl ]; then
    /usr/local/opt/openssl@1.1/bin/openssl "$@"
  elif [ -f /usr/local/opt/openssl/bin/openssl ]; then
    /usr/local/opt/openssl/bin/openssl "$@"
  else
    openssl "$@"
  fi
}

m_sed() {
  if which gsed > /dev/null 2>&1; then
    gsed "$@"
  else
    sed "$@"
  fi
}

awsStringSign4() {
  kSecret="AWS4$1"
  kDate=$(printf         '%s' "$2" | m_openssl dgst -sha256 -hex -mac HMAC -macopt "key:${kSecret}"     2>/dev/null | m_sed 's/^.* //')
  kRegion=$(printf       '%s' "$3" | m_openssl dgst -sha256 -hex -mac HMAC -macopt "hexkey:${kDate}"    2>/dev/null | m_sed 's/^.* //')
  kService=$(printf      '%s' "$4" | m_openssl dgst -sha256 -hex -mac HMAC -macopt "hexkey:${kRegion}"  2>/dev/null | m_sed 's/^.* //')
  kSigning=$(printf 'aws4_request' | m_openssl dgst -sha256 -hex -mac HMAC -macopt "hexkey:${kService}" 2>/dev/null | m_sed 's/^.* //')
  signedString=$(printf  '%s' "$5" | m_openssl dgst -sha256 -hex -mac HMAC -macopt "hexkey:${kSigning}" 2>/dev/null | m_sed 's/^.* //')
  printf '%s' "${signedString}"
}

iniGet() {
  # based on: https://stackoverflow.com/questions/22550265/read-certain-key-from-certain-section-of-ini-file-sed-awk#comment34321563_22550640
  printf '%s' "$(m_sed -n -E "/\[$2\]/,/\[.*\]/{/$3/s/(.*)=[ \\t]*(.*)/\2/p}" "$1")"
}

# Initialize access keys

if [ -z "${AWS_CONFIG_FILE:-}" ]; then
  if [ -z "${AWS_ACCESS_KEY_ID:-}" ]; then
    echo 'AWS_CONFIG_FILE or AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY envvars not set.'
    exit 1
  else
    awsAccess="${AWS_ACCESS_KEY_ID}"
    awsSecret="${AWS_SECRET_ACCESS_KEY}"
    awsRegion='us-east-1'
  fi
else
  awsProfile='default'

  # Read standard aws-cli configuration file
  # pointed to by the envvar AWS_CONFIG_FILE
  awsAccess="$(iniGet "${AWS_CONFIG_FILE}" "${awsProfile}" 'aws_access_key_id')"
  awsSecret="$(iniGet "${AWS_CONFIG_FILE}" "${awsProfile}" 'aws_secret_access_key')"
  awsRegion="$(iniGet "${AWS_CONFIG_FILE}" "${awsProfile}" 'region')"
fi

# Initialize defaults

fileName="${fileLocal##*/}"
fileRemote="${remotepath%/}/${fileName}" # strip a trailing slash from the remote path and add the filename
fileRemote=$(printf '%s' "${fileRemote}" | m_sed 's/ /%20/g')

if [ -z "${region}" ]; then
  region="${awsRegion}"
fi

echo "Uploading" "${fileLocal}" "->" "${bucket}" "${region}" "${storageClass}"
#echo "| $(uname) | $(m_openssl version) | $(m_sed --version | head -1) |"

# Initialize helper variables
httpReq='PUT'
authType='AWS4-HMAC-SHA256'
service='s3'
baseUrl=".${service}.amazonaws.com"
dateValueS=$(date -u +'%Y%m%d')
dateValueL=$(date -u +'%Y%m%dT%H%M%SZ')
if hash file 2>/dev/null; then
  contentType="$(file -b --mime-type "${fileLocal}")"
else
  contentType='application/octet-stream'
fi

# 0. Hash the file to be uploaded

if [ -f "${fileLocal}" ]; then
  payloadHash=$(m_openssl dgst -sha256 -hex < "${fileLocal}" 2>/dev/null | m_sed 's/^.* //')
else
  echo "File not found: '${fileLocal}'"
  exit 1
fi

# 1. Create canonical request

# NOTE: order significant in ${headerList} and ${canonicalRequest}

headerList='content-type;host;x-amz-content-sha256;x-amz-date;x-amz-server-side-encryption;x-amz-storage-class'

canonicalRequest="\
${httpReq}
/${fileRemote}

content-type:${contentType}
host:${bucket}${baseUrl}
x-amz-content-sha256:${payloadHash}
x-amz-date:${dateValueL}
x-amz-server-side-encryption:AES256
x-amz-storage-class:${storageClass}

${headerList}
${payloadHash}"

# Hash it
canonicalRequestHash=$(printf '%s' "${canonicalRequest}" | m_openssl dgst -sha256 -hex 2>/dev/null | m_sed 's/^.* //')

# 2. Create string to sign
stringToSign="\
${authType}
${dateValueL}
${dateValueS}/${region}/${service}/aws4_request
${canonicalRequestHash}"

# 3. Sign the string

signature=$(awsStringSign4 "${awsSecret}" "${dateValueS}" "${region}" "${service}" "${stringToSign}")

# Upload

curl -s -L --proto-redir =https -X "${httpReq}" -T "${fileLocal}" \
  -H "Content-Type: ${contentType}" \
  -H "Host: ${bucket}${baseUrl}" \
  -H "X-Amz-Content-SHA256: ${payloadHash}" \
  -H "X-Amz-Date: ${dateValueL}" \
  -H "X-Amz-Server-Side-Encryption: AES256" \
  -H "X-Amz-Storage-Class: ${storageClass}" \
  -H "Authorization: ${authType} Credential=${awsAccess}/${dateValueS}/${region}/${service}/aws4_request, SignedHeaders=${headerList}, Signature=${signature}" \
  "https://${bucket}${baseUrl}/${fileRemote}"

