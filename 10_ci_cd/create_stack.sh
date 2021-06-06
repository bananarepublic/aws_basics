#!/bin/bash

aws cloudformation create-stack --stack-name TK-CI-CD-Stack --template-body file://tk_ci_cd_stack.yaml --capabilities CAPABILITY_IAM --profile admin