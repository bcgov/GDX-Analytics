#!/usr/bin/env bash
usage() { echo "Usage: generateMFASecurityToken.sh [-m <mfa_profile>] <base_profile> <mfa_code>" 1>&2; exit 1; }
MFA_PROFILE_NAME="mfa"
# parse options
while getopts ":m:" o; do
    case "${o}" in
        m)
            MFA_PROFILE_NAME=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))
BASE_PROFILE_NAME=$1
TOKEN_CODE=$2
if [ -z "${BASE_PROFILE_NAME}" ] || [ -z "${TOKEN_CODE}" ]; then
    usage
fi

# Set default region
DEFAULT_REGION="ca-central-1"

# Set default output
DEFAULT_OUTPUT="json"

# MFA Serial: Specify MFA_SERIAL of IAM User
# Example: arn:aws:iam::123456789123:mfa/iamusername
MFA_SERIAL=`aws configure get mfa-serial --profile $BASE_PROFILE_NAME`

echo "Generating new IAM STS Token ..."
read -r AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN EXPIRATION < <(aws sts get-session-token --profile $BASE_PROFILE_NAME --output text --query 'Credentials.*' --serial-number $MFA_SERIAL --token-code $TOKEN_CODE)
if [ $? -ne 0 ];then
    echo "An error occured. Profile $MFA_PROFILE_NAME not updated"
else
    aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY" --profile $MFA_PROFILE_NAME
    aws configure set aws_session_token "$AWS_SESSION_TOKEN" --profile $MFA_PROFILE_NAME
    aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID" --profile $MFA_PROFILE_NAME
    aws configure set expiration "$EXPIRATION" --profile $MFA_PROFILE_NAME
    aws configure set region "$DEFAULT_REGION" --profile $MFA_PROFILE_NAME
    aws configure set output "$DEFAULT_OUTPUT" --profile $MFA_PROFILE_NAME
    echo "STS Session Token generated and saved in profile $MFA_PROFILE_NAME successfully."
fi