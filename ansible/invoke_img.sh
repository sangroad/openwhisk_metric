#!/bin/bash
curl -X POST -H "Content-Type: image/png" --data-binary @./wongi.png https://10.150.21.197/api/v1/namespaces/guest/actions/img -k -v
