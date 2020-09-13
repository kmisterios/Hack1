curl -X POST -H "Authorization: Bearer ${IAM_TOKEN}"  --data-binary "@voice.ogg"  "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId=${FOLDER_ID}"
