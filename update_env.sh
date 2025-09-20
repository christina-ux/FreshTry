#\!/bin/bash
cd ~/policyedgeai
secret=$(openssl rand -hex 32)
sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$secret/g" .env
cat .env
